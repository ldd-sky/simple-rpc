package org.school.work.config;

import lombok.Data;

/**
 * <p>Description: 注册中心配置</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月01日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
@Data
public class RegistryConfig {

    /**
     * 注册中心类别
     */
    private String registry = "etcd";

    /**
     * 注册中心地址
     */
    private String address = "http://localhost:2380";

    /**
     * 用户名
     */
    private String username;

    /**
     * 密码
     */
    private String password;

    /**
     * 超时时间（单位毫秒）
     */
    private Long timeout = 10000L;
}