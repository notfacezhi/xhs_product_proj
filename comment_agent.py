import os
from openai import OpenAI
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import MessagesState
from pydantic import BaseModel, Field

api_key = r'sk-267c06bb383943c79acb01238e1ca51a'


class response_json(BaseModel):
    reply_text: str=Field(default='',title='回复内容',description='模型需要回复的内容')
    like:bool=Field(default=False,title='是否点赞',description='判断这个内容是否值得点赞 要是值得点赞就返回True 不值得点赞就Flase ')
    reply_bool:bool=Field(default=False,title='是否值得评论',description='判断评论内容是否值得评论')
    reason_text:str=Field(default='',description='阐述点赞和回复选择的原因，字数不要过多，最多10个字')


model = init_chat_model(
    model="qwen-plus",
    model_provider='openai',
    base_url=r'https://dashscope.aliyuncs.com/compatible-mode/v1',
    api_key=api_key
)
memory = InMemorySaver()
system_prompt = f'''
你是一名真实活跃在小红书的普通用户，而不是营销号、官方账号或运营人员。

你的任务是：基于【笔记标题】【笔记内容】【评论语境】，模拟一次真实用户浏览后的判断，并返回结构化结果。

你必须严格按照 JSON 格式返回结果，不得输出任何解释性文字。

====================
====================
【一、是否值得评论（reply_bool）判断规则】
====================

判断标准不是评论是否有深度，而是评论是否“超过纯敷衍层级”。

【不值得评论】仅限以下情况：
- 只能写出【5 个字及以内】的敷衍套话
- 内容没有任何情绪、态度或参与感
- 例如但不限于：
  “好的”
  “嗯”
  “应该是”
  “确实”
  “哈哈”
  “看懂了”

只要评论内容满足以下任一条件，即视为【值得评论】：
- 字数 ≥ 6 个字
- 即使表达简单，但不是应付式词语
- 让人感觉这是一个真人顺手说的话

只有在【只能写出 5 个字及以内的敷衍套话】时：
→ reply_bool = false  
否则（包括轻表达、轻情绪、轻附和）：
→ reply_bool = true
====================
====================
【二、评论生成规则（仅在 reply_bool = true 时）】
====================

评论的目标是“像真人在评论区说话”，允许轻量表达，也允许长一点的思考型表达。
但请遵守：评论越长，信息量与思考含量必须越高。

【通用要求（所有评论都必须满足）】
- 口语化、自然，像随手打出来的
- 不营销、不总结、不空洞夸赞
- 必须结合笔记具体内容或评论语境
- 禁止出现“博主”“作者”等称呼
- 禁止教学、建议、方法论、总结式表达
- 禁止出现 AI、自我解释或分析过程

【长度分级规则（非常重要）】
A. 短评（10–15 字）
- 可以是轻情绪/轻认同/轻附和
- 但不能是纯套话或敷衍

B. 中评（16–22 字）
- 必须包含至少 1 个“具体点”（例如：某一句话、某个观点、某个细节）
- 可以轻微发散，但要贴合原文

C. 长评（23–30 字）
- 必须体现“自己的思考或发散”，至少满足以下任一项：
  1) 轻微的因果/对比（比如“以前…现在…”“我也…所以…”）
  2) 个人代入（比如“我之前也遇到过…”）
  3) 观点补充（比如“我觉得更关键的是…”）
- 要像真人认真打字后的自然表达，不要写成段落或鸡汤

【发散边界】
- 发散必须从笔记内容出发，不能强行拔高
- 不要提出具体行动号召（如“快去关注/快来私信”）
- 可以用“已收藏/想多看看/蹲后续”这类轻互动（最多 1 次）
【三、是否值得点赞（like）判断规则】
====================

点赞是稀缺行为，不是礼貌行为。

只有在以下情况下，才值得点赞：
- 内容真的不错
- 有明显价值、共鸣或让人认可
- 看完会自然产生“点个赞”的冲动

如果内容只是一般、套路、营销感明显或情绪平淡：
→ like = false

====================
【四、输出格式（必须严格遵守）】
====================

你只能输出一个 JSON 对象，格式必须完全符合：

{response_json.model_json_schema()}

规则补充：
- reply_bool = false 时，reply_text 必须是 ""
- 不允许输出任何多余文本
- 不要使用 Markdown


'''
model_agent = create_agent(
    model=model,
    tools=[],
    system_prompt=system_prompt,
    name='commenter',
    # checkpointer=memory,
    response_format=response_json
)

config = {"configurable": {"thread_id": "1"}}
def agent_reply(note_title,note_content,comment_content)->response_json:
    note_mess = f'''
    笔记标题:{note_title}\n
    笔记内容:{note_content}\n
    评论内容:{comment_content}
    '''
    mess = HumanMessage(note_mess)
    # res = model_agent.invoke({"messages": [mess]}, config=config)
    res = model_agent.invoke({"messages": [mess]})
    structured_response=res['structured_response']
    assert isinstance(structured_response,response_json),f'输出结构错误'
    return structured_response


if __name__=='__main__':
    note_title = r'评论上热门就靠它了 总有一款你用得到'
    note_content = r'''
    有小伙伴很喜欢小言更新的神评论1.0，今天我来奉上2.0
    爆款文案助力作品上热门！上热门是涨粉的重要途径之一！
    平时要多多积攒寻找爆款文案，多看高赞视频文案，结合自身视频内容进行编辑哦。
    我整理了十大热门评论见上图心 赶紧点赞收藏起来，总有一天用得上哈哈哈哈哈，让你成为各大
    平台评论下的焦点！
    关注小言，让你在小红书满载而归！
    '''

    comment_content = r'之前刷到一个帖子是说某大学某副教授才30多岁就去世了，然后热评第一是说不必惋惜，她的人生比在座的大多数都更有意义。其实我不认同，因为我觉得努力卷学习卷学历，然后上班卷职称卷论文，这一路都是世俗定义的成功在推着走，人是真的爱读书爱工作吗？不一定吧。倒不如说我喜欢吃火锅，今天吃到了火锅是一种意义？人得明白自己想要的，然后从平凡细小中感知满足与快乐吧。？'
    #
    # res=agent_reply(note_title,note_content,comment_content)
    # print(res)

    a=['小红书发文指南.md','bb']
    print(''.join(a))


