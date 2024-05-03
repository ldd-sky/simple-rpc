package org.school.work.server.tcp;

import io.vertx.core.Vertx;
import io.vertx.core.buffer.Buffer;
import io.vertx.core.net.NetServer;
import org.school.work.server.HttpServer;

/**
 * <p>Description: TCp 服务器</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class VertxTcpServer implements HttpServer {

    private byte[] handleRequest(byte[] requestData){
        // 编写处理请求的逻辑，根据 requestData构造响应数据并返回
        // 这里仅仅是一个示例
        return "Hello, client!".getBytes();
    }

    @Override
    public void doStart(int port) {
        Vertx vertx = Vertx.vertx();

        NetServer server = vertx.createNetServer();

        // 处理请求
        server.connectHandler(socket -> {
            // 处理连接
            socket.handler(buffer -> {
               // 处理收到的字节数组
                byte[] requestData = buffer.getBytes();
               // 在这里进行自定义的字节数组处理逻辑，比如解析请求、调用服务、构造响应
                byte[] responseData = handleRequest(requestData);
                // 发送响应
                socket.write(Buffer.buffer(responseData));
            });
        });

        // 启动TCP服务器并监听指定端口
        server.listen(port, result->{
           if(result.succeeded()){
               System.out.println("TCP server started on port " + port);
           } else {
               System.err.println("Failed to start TCP server: " + result.cause());
           }
        });
    }

    public static void main(String[] args) {
        new VertxTcpServer().doStart(8888);
    }
}