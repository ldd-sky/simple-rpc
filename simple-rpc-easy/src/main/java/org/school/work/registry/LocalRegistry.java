package org.school.work.registry;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * <p>Description: 本地注册中心</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年04月30日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class LocalRegistry {
    /**
     * 注册信息存储
     */
    public static final Map<String, Class<?>> map = new ConcurrentHashMap<>();

    /**
     * 注册服务
     * @param serviceName 服务名
     * @param implClass 服务对应的实现类
     */
    public static void register(String serviceName, Class<?> implClass){
        map.put(serviceName, implClass);
    }

    /**
     * 获取服务
     * @param serviceName 服务名
     * @return 服务对应的实现类
     */
    public static Class<?> get(String serviceName){
        return map.get(serviceName);
    }

    /**
     * 删除服务
     * @param serviceName 服务名
     */
    public static void remove(String serviceName){
        map.remove(serviceName);
    }
}