package org.school.work.server.tcp;

import io.vertx.core.Vertx;

/**
 * <p>Description: TCP 客户端</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class VertxTcoClient {

    public void start(){
        Vertx vertx = Vertx.vertx();

        vertx.createNetClient().connect(8888, "localhost", result -> {
           if(result.succeeded()){
               System.out.println("Connected to TCP server");
               io.vertx.core.net.NetSocket socket = result.result();
               // 发送数据
               socket.write("Hello, server!");
               // 接受响应
               socket.handler(buffer -> {
                   System.out.println("Received response from server: " + buffer.toString());
               });
           } else {
               System.err.println("Failed to connect to TCP server");
           }
        });
    }

    public static void main(String[] args) {
        new VertxTcoClient().start();
    }
}