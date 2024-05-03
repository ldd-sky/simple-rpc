package org.school.work;

import org.school.work.bootstrap.ProviderBootstrap;
import org.school.work.config.RegistryConfig;
import org.school.work.config.RpcConfig;
import org.school.work.model.ServiceMetaInfo;
import org.school.work.model.ServiceRegisterInfo;
import org.school.work.proxy.RegistryFactory;
import org.school.work.registry.LocalRegistry;
import org.school.work.registry.Registry;
import org.school.work.server.HttpServer;
import org.school.work.server.VertxHttpServer;
import org.school.work.service.UserService;

import java.util.ArrayList;
import java.util.List;

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
        // 要注册的服务
        List<ServiceRegisterInfo<?>> serviceRegisterInfoList = new ArrayList<>();
        ServiceRegisterInfo<UserService> serviceRegisterInfo = new ServiceRegisterInfo<>(UserService.class.getName(), UserServiceImpl.class);
        serviceRegisterInfoList.add(serviceRegisterInfo);

        // 服务提供者初始化
        ProviderBootstrap.init(serviceRegisterInfoList);
    }
}