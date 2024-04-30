package org.school.work.server;

import io.vertx.core.Handler;
import io.vertx.core.buffer.Buffer;
import io.vertx.core.http.HttpServerRequest;
import io.vertx.core.http.HttpServerResponse;
import org.school.work.RpcApplication;
import org.school.work.model.RpcRequest;
import org.school.work.model.RpcResponse;
import org.school.work.registry.LocalRegistry;
import org.school.work.serializer.Serializer;
import org.school.work.serializer.SerializerFactory;

import java.io.IOException;
import java.lang.reflect.Method;

/**
 * <p>Description: HTTP请求处理</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年04月30日</P>
 *
 * 1. 反序列化请求为对象，并从请求对象中获取参数。
 * 2. 根据服务名称从本地注册器中获取到对应的服务实现类。
 * 3. 通过反射机制调用方法，得到返回结果。
 * 4. 对返回结果进行封装和序列化，并写入到响应中。
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class HttpServerHandler implements Handler<HttpServerRequest> {
    @Override
    public void handle(HttpServerRequest request) {
        // 指定序列化器
        final Serializer serializer = SerializerFactory.getInstance(RpcApplication.getRpcConfig().getSerializer());

        // 记录日志
        System.out.println("Received request: " + request.method() + " " + request.uri());

        // 异步处理HTTP请求
        request.bodyHandler(body -> {
            byte[] bytes = body.getBytes();
            RpcRequest rpcRequest;
            try {
                rpcRequest = serializer.deserialize(bytes, RpcRequest.class);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }

            // 构造响应结果对象
            RpcResponse rpcResponse = new RpcResponse();

            try {
                // 通过反射获取要调用的服务实现类
                Class<?> implClass = LocalRegistry.get(rpcRequest.getServiceName());
                Method method = implClass.getMethod(rpcRequest.getMethodName(), rpcRequest.getParameterTypes());
                Object result = method.invoke(implClass.getDeclaredConstructor().newInstance(), rpcRequest.getArgs());
                // 封装返回结果
                rpcResponse.setData(result);
                rpcResponse.setDataType(method.getReturnType());
                rpcResponse.setMessage("ok");
            } catch (Exception e) {
                e.printStackTrace();
                rpcResponse.setMessage(e.getMessage());
                rpcResponse.setException(e);
            }

        });
    }

    /**
     * 响应
     */
    void doResponse(HttpServerRequest request, RpcResponse rpcResponse, Serializer serializer){
        HttpServerResponse httpServerResponse = request.response()
                .putHeader("content-type", "application/json");
        try {
            // 序列化
            byte[] serialized = serializer.serialize(rpcResponse);
            httpServerResponse.end(Buffer.buffer(serialized));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}