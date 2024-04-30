package org.school.work.serializer;

import org.school.work.spi.SpiLoader;

/**
 * <p>Description: 序列化工厂</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月01日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class SerializerFactory {

    static {
        SpiLoader.load(Serializer.class);
    }

    /**
     * 默认序列化器
     */
    public static final Serializer DEFAULT_SERIALIZER = new JdkSerializer();

    /**
     * 获取实例
     */
    public static Serializer getInstance(String key){
        return SpiLoader.getInstance(Serializer.class, key);
    }
}