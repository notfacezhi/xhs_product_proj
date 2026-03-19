"""
启动小红书监控后端服务
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("小红书监控后端服务启动中...")
    print("API地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("=" * 50)

    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
