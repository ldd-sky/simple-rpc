package org.school.work.loadbalancer;

import org.school.work.model.ServiceMetaInfo;

import java.util.List;
import java.util.Map;

/**
 * <p>Description: 负载均衡器（消费端使用）</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public interface LoadBalancer {
    /**
     * 选择服务调用
     */
    ServiceMetaInfo select(Map<String, Object> requestParams, List<ServiceMetaInfo> serviceMetaInfoList);
}