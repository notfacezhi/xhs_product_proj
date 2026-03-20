-- 创建数据库
CREATE DATABASE IF NOT EXISTS xhs_data DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE xhs_data;

-- 创建小红书笔记表
CREATE TABLE IF NOT EXISTS xhs_notes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    note_id VARCHAR(50) NOT NULL UNIQUE COMMENT '笔记唯一标识',
    note_url VARCHAR(500) NOT NULL COMMENT '笔记链接',
    title VARCHAR(500) NOT NULL COMMENT '笔记标题',
    `desc` TEXT COMMENT '笔记正文描述',
    author_name VARCHAR(100) NOT NULL COMMENT '作者昵称',
    author_url VARCHAR(500) COMMENT '作者主页链接',
    publish_time VARCHAR(50) COMMENT '发布时间',
    like_count VARCHAR(20) COMMENT '点赞数',
    keyword VARCHAR(100) COMMENT '搜索关键词',
    type VARCHAR(20) DEFAULT 'normal' COMMENT '笔记类型(normal/video)',
    images JSON COMMENT '图片列表(JSON)',
    video_url TEXT COMMENT '视频URL',
    tags JSON COMMENT '标签列表(JSON)',
    topic VARCHAR(200) COMMENT '话题名称',
    ip_location VARCHAR(100) COMMENT 'IP归属地',
    collected_count VARCHAR(20) COMMENT '收藏数',
    share_count VARCHAR(20) COMMENT '分享数',
    comment_count VARCHAR(20) COMMENT '评论数',
    is_comment_crawled TINYINT(1) DEFAULT 0 COMMENT '是否已爬取评论(0:未爬取,1:已爬取)',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
    INDEX idx_note_id (note_id),
    INDEX idx_keyword (keyword),
    INDEX idx_author_name (author_name),
    INDEX idx_create_time (create_time),
    INDEX idx_is_comment_crawled (is_comment_crawled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='小红书笔记数据表';

-- 创建小红书评论表
CREATE TABLE IF NOT EXISTS xhs_comments (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    note_id VARCHAR(50) NOT NULL COMMENT '笔记ID',
    note_url VARCHAR(500) NOT NULL COMMENT '笔记链接',
    comment_content TEXT NOT NULL COMMENT '评论内容',
    keyword VARCHAR(100) COMMENT '搜索关键词',
    collect_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '收集时间',
    INDEX idx_note_id (note_id),
    INDEX idx_keyword (keyword),
    INDEX idx_collect_time (collect_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='小红书评论数据表';

-- 创建笔记AI回复记录表（旧版-通用评论）
CREATE TABLE IF NOT EXISTS xhs_note_agent_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    note_id VARCHAR(50) NOT NULL COMMENT '笔记ID',
    note_title VARCHAR(500) COMMENT '笔记标题',
    note_desc TEXT COMMENT '笔记描述',
    comment_content TEXT NOT NULL COMMENT '用户评论内容',
    reply_text TEXT COMMENT 'AI回复内容',
    is_like TINYINT(1) DEFAULT 0 COMMENT '是否点赞(0:否,1:是)',
    reply_bool TINYINT(1) DEFAULT 0 COMMENT '是否值得评论(0:否,1:是)',
    reason_text VARCHAR(100) DEFAULT '' COMMENT '点赞和回复选择的原因',
    keyword VARCHAR(100) COMMENT '搜索关键词',
    reply_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'AI回复时间',
    INDEX idx_note_id (note_id),
    INDEX idx_keyword (keyword),
    INDEX idx_reply_time (reply_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='笔记AI回复记录表';

-- 创建需求调研记录表（新版-精准营销）
CREATE TABLE IF NOT EXISTS xhs_demand_research_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    note_id VARCHAR(50) NOT NULL COMMENT '笔记ID',
    note_title VARCHAR(500) COMMENT '笔记标题',
    note_desc TEXT COMMENT '笔记描述',
    comment_content TEXT NOT NULL COMMENT '用户评论内容',
    is_newcomer TINYINT(1) DEFAULT 0 COMMENT '是否运营新人(0:否,1:是)',
    has_launch_intent TINYINT(1) DEFAULT 0 COMMENT '是否有起号意图(0:否,1:是)',
    demand_level VARCHAR(20) DEFAULT '无需求' COMMENT '需求等级(无需求/潜在需求/强需求)',
    reply_text TEXT COMMENT 'AI调研回复内容',
    reason VARCHAR(100) DEFAULT '' COMMENT '需求判断原因',
    is_like TINYINT(1) DEFAULT 0 COMMENT '是否点赞(0:否,1:是)',
    reply_bool TINYINT(1) DEFAULT 0 COMMENT '是否实际回复(0:否,1:是)',
    keyword VARCHAR(100) COMMENT '搜索关键词',
    reply_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'AI回复时间',
    INDEX idx_note_id (note_id),
    INDEX idx_keyword (keyword),
    INDEX idx_demand_level (demand_level),
    INDEX idx_is_newcomer (is_newcomer),
    INDEX idx_has_launch_intent (has_launch_intent),
    INDEX idx_reply_time (reply_time),
    INDEX idx_high_value_user (is_newcomer, has_launch_intent, demand_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='需求调研记录表-用于精准识别潜在客户';
