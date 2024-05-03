package org.school.work.proxy;

import cn.hutool.core.collection.CollUtil;
import org.school.work.RpcApplication;
import org.school.work.config.RpcConfig;
import org.school.work.constant.RpcConstant;
import org.school.work.fault.retry.RetryStrategy;
import org.school.work.fault.retry.RetryStrategyFactory;
import org.school.work.loadbalancer.LoadBalancer;
import org.school.work.loadbalancer.LoadBalancerFactory;
import org.school.work.model.RpcRequest;
import org.school.work.model.RpcResponse;
import org.school.work.model.ServiceMetaInfo;
import org.school.work.registry.Registry;
import org.school.work.serializer.Serializer;
import org.school.work.serializer.SerializerFactory;
import org.school.work.server.tcp.VertxTcpClient;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * <p>Description: JDK动态服务代理</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年04月30日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class ServiceProxy implements InvocationHandler {
    /**
     * 调用代理
     */
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) {
        // 指定序列化器
        final Serializer serializer = SerializerFactory.getInstance(RpcApplication.getRpcConfig().getSerializer());

        // 构造请求
        String serviceName = method.getDeclaringClass().getName();
        RpcRequest rpcRequest = RpcRequest.builder()
                .serviceName(method.getDeclaringClass().getName())
                .methodName(method.getName())
                .parameterTypes(method.getParameterTypes())
                .args(args)
                .build();

        try {
            // 从注册中心获取服务提供者请求地址
            RpcConfig rpcConfig = RpcApplication.getRpcConfig();
            Registry registry = RegistryFactory.getInstance(rpcConfig.getRegistryConfig().getRegistry());
            ServiceMetaInfo serviceMetaInfo = new ServiceMetaInfo();
            serviceMetaInfo.setServiceName(serviceName);
            serviceMetaInfo.setServiceVersion(RpcConstant.DEFAULT_SERVICE_VERSION);
            List<ServiceMetaInfo> serviceMetaInfoList = registry.serviceDiscovery(serviceMetaInfo.getServiceKey());
            if (CollUtil.isEmpty(serviceMetaInfoList)){
                throw new RuntimeException("暂无服务地址");
            }

            // 负载均衡
            LoadBalancer loadBalancer = LoadBalancerFactory.getInstance(rpcConfig.getLoadBalancer());
            // 将调用方法名（请求路径）作为负载均衡参数
            Map<String, Object> requestParams = new HashMap<>();
            requestParams.put("methodName", rpcRequest.getMethodName());
            ServiceMetaInfo selectedServiceMetaInfo = loadBalancer.select(requestParams, serviceMetaInfoList);

            // rpc请求，使用重试机制
            RetryStrategy retryStrategy = RetryStrategyFactory.getInstance(rpcConfig.getRetryStrategy());
            RpcResponse rpcResponse = retryStrategy.doRetry(() ->
                    VertxTcpClient.doRequest(rpcRequest, selectedServiceMetaInfo)
            );
            return rpcResponse.getData();
        } catch (Exception e){
            throw new RuntimeException("调用失败");
        }
    }
}