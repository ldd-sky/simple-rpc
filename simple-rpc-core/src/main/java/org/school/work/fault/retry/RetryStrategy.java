package org.school.work.fault.retry;

import org.school.work.model.RpcResponse;

import java.util.concurrent.Callable;

/**
 * <p>Description: 重试策略</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public interface RetryStrategy {
    /**
     * 重试
     */
    RpcResponse doRetry(Callable<RpcResponse> callable) throws Exception;
}