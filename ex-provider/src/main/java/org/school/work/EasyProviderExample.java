package org.school.work;

import org.school.work.registry.LocalRegistry;
import org.school.work.server.HttpServer;
import org.school.work.server.VertxHttpServer;
import org.school.work.service.UserService;

/**
 * <p>Description: 简单的服务提供者示例</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年04月30日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class EasyProviderExample {
    public static void main(String[] args) {
        // RPC框架初始化
        RpcApplication.init();

        // 注册服务
        LocalRegistry.register(UserService.class.getName(), UserServiceImpl.class);

        // 启动Web服务
        HttpServer httpServer = new VertxHttpServer();
        httpServer.doStart(RpcApplication.getRpcConfig().getServerPort());
    }
}