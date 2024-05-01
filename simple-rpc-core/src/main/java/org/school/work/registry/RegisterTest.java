package org.school.work.registry;

import org.school.work.config.RegistryConfig;
import org.school.work.model.ServiceMetaInfo;
import org.junit.*;

/**
 * <p>Description: 注册中心测试</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月01日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class RegisterTest {
    final Registry registry = new EtcdRegistry();

    @Before
    public void init() {
        RegistryConfig registryConfig = new RegistryConfig();
        registryConfig.setAddress("http://localhost:2379");
        registry.init(registryConfig);
    }
    @Test
    public void register() throws Exception {
        ServiceMetaInfo serviceMetaInfo = new ServiceMetaInfo();
        serviceMetaInfo. setServiceName ("myService");
        serviceMetaInfo. setServiceVersion("1.0");
        serviceMetaInfo. setServiceHost ("localhost");
        serviceMetaInfo. setServicePort (1234);
        registry.register(serviceMetaInfo);
        serviceMetaInfo = new ServiceMetaInfo();
        serviceMetaInfo.setServiceName ("myService");
        serviceMetaInfo.setServiceVersion("1.0");
        serviceMetaInfo.setServiceHost ("localhost");
        serviceMetaInfo. setServicePort (1235);
        registry. register(serviceMetaInfo);
        serviceMetaInfo = new ServiceMetaInfo();
        serviceMetaInfo. setServiceName ("myService");
        serviceMetaInfo. setServiceVersion("2.0");
        serviceMetaInfo. setServiceHost ("localhost");
        serviceMetaInfo. setServicePort (1234);
        registry. register(serviceMetaInfo);
    }


    @Test
    public void unRegister() {
        ServiceMetaInfo serviceMetaInfo = new ServiceMetaInfo();
        serviceMetaInfo.setServiceName ("myService");
        serviceMetaInfo. setServiceVersion("1.0");
        serviceMetaInfo. setServiceHost ("localhost");
        serviceMetaInfo. setServicePort (1234);
        registry.unRegister(serviceMetaInfo);
    }

    @Test
    public void heartBeat() throws Exception{
        register();
        Thread.sleep(60 * 1000L);
    }
}