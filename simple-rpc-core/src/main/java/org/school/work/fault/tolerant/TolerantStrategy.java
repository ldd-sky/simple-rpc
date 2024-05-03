package org.school.work.fault.tolerant;

import org.school.work.model.RpcResponse;

import java.util.Map;

/**
 * <p>Description: 容错策略</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public interface TolerantStrategy {
    /**
     * 容错
     * @param context   上下文，传递数据
     * @param e         异常
     */
    RpcResponse doTolerant(Map<String, Object> context, Exception e);
}