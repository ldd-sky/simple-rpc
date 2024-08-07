package org.school.work.proxy;

import org.school.work.RpcApplication;

import java.lang.reflect.Proxy;

/**
 * <p>Description: 工厂设计模式：服务代理工厂，用于创建代理对象</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年04月30日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class ServiceProxyFactory {

    /**
     * 根据服务类获取代理对象
     */
    @SuppressWarnings("unchecked")
    public static <T> T getProxy(Class<T> serviceClass){
        if (RpcApplication.getRpcConfig().isMock()){
            return getMockProxy(serviceClass);
        }

        return (T) Proxy.newProxyInstance(
                serviceClass.getClassLoader(),
                new Class[]{serviceClass},
                new ServiceProxy()
        );
    }

    /**
     * 根据服务类获取 Mock 代理对象
     */
    @SuppressWarnings("unchecked")
    public static <T> T getMockProxy(Class<T> serviceClass){
        return (T) Proxy.newProxyInstance(
                serviceClass.getClassLoader(),
                new Class[]{serviceClass},
                new MockServiceProxy()
        );
    }
}