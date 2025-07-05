// 创建数据库用户
db = db.getSiblingDB('long-quant');

db.createUser({
  user: 'user',
  pwd: 'password',
  roles: [
    {
      role: 'readWrite',
      db: 'long-quant'
    }
  ]
});

// 创建基础集合
db.createCollection('stocks');
db.createCollection('news');
db.createCollection('analysis');
db.createCollection('logs');

// 为stocks集合创建索引
db.stocks.createIndex({ "code": 1 }, { unique: true });
db.stocks.createIndex({ "name": 1 });

// 为news集合创建索引
db.news.createIndex({ "title": 1 });
db.news.createIndex({ "publish_time": -1 });
db.news.createIndex({ "source": 1 });

// 为analysis集合创建索引
db.analysis.createIndex({ "stock_code": 1 });
db.analysis.createIndex({ "created_at": -1 });

// 为logs集合创建索引
db.logs.createIndex({ "timestamp": -1 });
db.logs.createIndex({ "level": 1 });

print('Database initialized successfully');
