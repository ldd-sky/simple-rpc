package org.school.work.server;

import io.vertx.core.Vertx;

/**
 * <p>Description: 基于Vert.x实现的Web服务器</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年04月30日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class VertxHttpServer implements HttpServer{
    @Override
    public void doStart(int port) {
        Vertx vertx = Vertx.vertx();
        // 创建HTTP服务器
        io.vertx.core.http.HttpServer server = vertx.createHttpServer();

//        server.requestHandler(request -> {
//            // 处理HTTP请求
//            System.out.println("Received request:" + request.method() + " " + request.uri());
//
//            // 发送HTTP响应
//            request.response()
//                    .putHeader("content-type", "text/plain")
//                    .end("Hello from Vert.x HTTP server!");
//        });

        // 监听端口并处理请求
        server.requestHandler(new HttpServerHandler());

        // 启动HTTP服务器并监听端口
        server.listen(port, result -> {
            if (result.succeeded()){
                System.out.println("Server is now listening on port " + port);
            } else {
                System.err.println("Failed to start server: " + result.cause());
            }
        });
    }
}