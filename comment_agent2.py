import os
from openai import OpenAI
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel, Field

# 建议通过环境变量读取API Key，更安全
# api_key = os.getenv("DASHSCOPE_API_KEY")
api_key = r'sk-267c06bb383943c79acb01238e1ca51a'


# 重新定义结构化输出模型，适配新的业务目标
class DemandResearchResponse(BaseModel):
    is_newcomer: bool = Field(default=False, title='是否运营新人', description='判断评论者是否是小红书起号新人，无运营经验')
    has_launch_intent: bool = Field(default=False, title='是否有起号意图', description='判断评论者是否有渴望起号、运营小红书的意图')
    reply_text: str = Field(default='', title='调研回复内容', description='若满足新人+起号意图，生成委婉的调研回复；否则为空')
    demand_level: str = Field(default='无需求', title='需求等级', description='可选：无需求/潜在需求/强需求，基于评论内容判断对AI起号工具的需求程度')
    reason: str = Field(default='', description='判断需求等级的原因，最多15字')


# 初始化通义千问模型
model = init_chat_model(
    model="qwen-plus",
    model_provider='openai',
    base_url=r'https://dashscope.aliyuncs.com/compatible-mode/v1',
    api_key=api_key
)

# 重构系统提示词，聚焦“新人识别+需求调研”
system_prompt = f'''
你是一名小红书运营需求调研分析师，专注于挖掘新人起号的痛点和AI工具的市场需求。

你的任务是：基于【笔记标题】【笔记内容】【评论内容】，完成以下判断并返回结构化结果：
1. 识别评论者是否是小红书运营新人（无起号/运营经验）；
2. 判断评论者是否有渴望起号、运营小红书的意图；
3. 若满足“新人+起号意图”，生成委婉的调研回复（询问是否愿意用AI自动批量起号工具）；
4. 基于评论内容判断对AI起号工具的需求等级（无需求/潜在需求/强需求）。

====================
【关键判断规则】
====================
1. 【运营新人判断】
   符合以下任一条件即为新人：
   - 评论中提及“不会起号”“新手”“刚做小红书”“不知道怎么开始”等；
   - 询问起号方法、流量技巧、运营思路等基础问题；
   - 表达起号难、没效果、没经验等。
   反之（如分享起号经验、指导他人）则不是新人。

2. 【起号意图判断】
   符合以下任一条件即为有意图：
   - 评论中表达想做小红书、想起号、想涨粉、想运营账号等；
   - 抱怨起号难但未放弃，仍想尝试；
   - 询问起号相关问题（本身就代表有意图）。

3. 【回复生成规则】
   - 语气：自然、共鸣式，像朋友间的闲聊吐槽，不能有任何营销感；
   - 内容：纯粹的共情+轻度发散想象，不要直接提问或询问意愿；
   - 字数：严格控制在20-30字左右，表达完整但不啰嗦；
   - 核心思路：表达"要是有XX就好了"的美好愿望，而不是"你要不要试试XX"的推销；
   - 禁止：任何疑问句、邀请句、推销句、"我司""产品""工具"等营销词汇；
   - 示例：
     ✅ 同感！我也是新手，每天手动运营太累了，要是有AI能自动帮忙就好了
     ✅ 真的好难啊，想内容想到头秃，感觉要是AI能自动发笔记就轻松多了
     ✅ 哈哈我也在摸索中，起号真的费时间，好希望有AI能批量操作
     ❌ 同感！要是有AI能自动运营就好了
     ❌ 你会愿意试试AI工具吗？

4. 【需求等级判断】
   - 无需求：非新人/无起号意图；
   - 潜在需求：是新人+有起号意图，但未表达强烈痛点；
   - 强需求：是新人+有起号意图，且抱怨起号难、效率低、没时间运营等强烈痛点。

====================
【输出格式要求】
====================
1. 只能输出JSON对象，格式严格匹配{DemandResearchResponse.model_json_schema()}；
2. 非新人/无起号意图时，reply_text必须为空；
3. 回复内容必须口语化、自然，符合小红书评论风格；
4. 禁止输出任何多余文本、解释性文字或Markdown。
'''

# 构建Agent
model_agent = create_agent(
    model=model,
    tools=[],
    system_prompt=system_prompt,
    name='demand_research_agent',
    response_format=DemandResearchResponse
)


# 核心调用函数
def research_demand(note_title, note_content, comment_content) -> DemandResearchResponse:
    # 精简输入格式，避免多余空格/换行影响模型判断
    input_message = f'''
    笔记标题：{note_title}
    笔记内容：{note_content}
    评论内容：{comment_content}
    '''.strip()

    # 封装为HumanMessage并调用Agent
    human_msg = HumanMessage(content=input_message)
    response = model_agent.invoke({"messages": [human_msg]})

    # 提取结构化结果并校验
    structured_res = response['structured_response']
    assert isinstance(structured_res, DemandResearchResponse), '输出结构不符合要求'
    return structured_res


# 测试代码
if __name__ == '__main__':
    # 测试用例1：强需求新人评论
    note_title = '小红书起号太难了？教你3个新手必看技巧'
    note_content = '新手做小红书，最容易踩的坑就是盲目发内容！分享3个起号小技巧，帮你少走弯路。'
    comment_content = '真的太难了😭我刚做小红书，完全不知道怎么起号，发了10条笔记都没流量，每天花好几个小时还是没效果，有没有省事点的方法啊？'

    # 测试用例2：无需求评论
    # note_title = '小红书起号太难了？教你3个新手必看技巧'
    # note_content = '新手做小红书，最容易踩的坑就是盲目发内容！分享3个起号小技巧，帮你少走弯路。'
    # comment_content = '我做小红书半年了，起号其实不难，关键是找对赛道，我现在每月能涨5000粉'

    # 调用调研函数
    res = research_demand(note_title, note_content, comment_content)
    # 打印结构化结果（可转为JSON用于统计）
    print("调研结果：")
    print(f"是否新人：{res.is_newcomer}")
    print(f"是否有起号意图：{res.has_launch_intent}")
    print(f"调研回复：{res.reply_text}")
    print(f"需求等级：{res.demand_level}")
    print(f"判断原因：{res.reason}")

    # 转为JSON格式（便于批量统计）
    print("\nJSON格式结果：")
    print(res.model_dump_json(indent=2))