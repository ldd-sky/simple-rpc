package org.school.work;

import org.school.work.config.RegistryConfig;
import org.school.work.config.RpcConfig;
import org.school.work.model.ServiceMetaInfo;
import org.school.work.proxy.RegistryFactory;
import org.school.work.registry.LocalRegistry;
import org.school.work.registry.Registry;
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
public class ProviderExample {

    public static void main(String[] args) {
        // RPC 框架初始化
        RpcApplication.init();

        // 注册服务
        String serviceName = UserService.class.getName();
        LocalRegistry.register(serviceName, UserServiceImpl.class);

        // 注册服务到注册中心
        RpcConfig rpcConfig = RpcApplication.getRpcConfig();
        RegistryConfig registryConfig = rpcConfig.getRegistryConfig();
        Registry registry = RegistryFactory.getInstance(registryConfig.getRegistry());
        ServiceMetaInfo serviceMetaInfo = new ServiceMetaInfo();
        serviceMetaInfo.setServiceName(serviceName);
        serviceMetaInfo.setServiceHost(rpcConfig.getServerHost());
        serviceMetaInfo.setServicePort(rpcConfig.getServerPort());
        try {
            registry.init(registryConfig);
            registry.register(serviceMetaInfo);
        } catch (Exception e){
            throw new RuntimeException(e);
        }

        // 启动web服务
        HttpServer httpServer = new VertxHttpServer();
        httpServer.doStart(RpcApplication.getRpcConfig().getServerPort());
    }
}