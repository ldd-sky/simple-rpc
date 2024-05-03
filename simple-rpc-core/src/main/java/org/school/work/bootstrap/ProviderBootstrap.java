package org.school.work.bootstrap;

import org.school.work.RpcApplication;
import org.school.work.config.RegistryConfig;
import org.school.work.config.RpcConfig;
import org.school.work.model.ServiceMetaInfo;
import org.school.work.model.ServiceRegisterInfo;
import org.school.work.proxy.RegistryFactory;
import org.school.work.registry.LocalRegistry;
import org.school.work.registry.Registry;
import org.school.work.server.HttpServer;
import org.school.work.server.VertxHttpServer;

import java.util.List;

/**
 * <p>Description: 服务提供者初始化</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class ProviderBootstrap {

    /**
     * 初始化
     */
    public static void init(List<ServiceRegisterInfo<?>> serviceRegisterInfoList){
        // RPC 框架初始化
        RpcApplication.init();
        // 全局配置
        final RpcConfig rpcConfig = RpcApplication.getRpcConfig();

        // 注册服务
        for (ServiceRegisterInfo<?> serviceRegisterInfo : serviceRegisterInfoList){
            String serviceName = serviceRegisterInfo.getServiceName();
            // 本地注册
            LocalRegistry.register(serviceName, serviceRegisterInfo.getImplClass());

            // 注册服务到注册中心
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
                throw new RuntimeException(serviceName + "服务注册失败", e);
            }
        }

        // 启动web服务
        HttpServer httpServer = new VertxHttpServer();
        httpServer.doStart(RpcApplication.getRpcConfig().getServerPort());
    }
}