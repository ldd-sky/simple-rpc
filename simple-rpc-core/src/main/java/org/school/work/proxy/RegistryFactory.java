package org.school.work.proxy;

import org.school.work.registry.EtcdRegistry;
import org.school.work.registry.Registry;
import org.school.work.spi.SpiLoader;

/**
 * <p>Description: 注册中心工厂（用于获取注册中心对象）</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月01日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class RegistryFactory {

    // SPI 动态加载
    static {
        SpiLoader.load(Registry.class);
    }

    /**
     * 默认注册中心
     */
    private static final Registry DEFAULT_REGISTRY = new EtcdRegistry();

    /**
     * 获取实例
     */
    public static Registry getInstance(String key){
        return SpiLoader.getInstance(Registry.class, key);
    }
}