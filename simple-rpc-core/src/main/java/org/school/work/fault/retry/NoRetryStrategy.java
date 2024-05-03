package org.school.work.fault.retry;

import org.school.work.model.RpcResponse;

import java.util.concurrent.Callable;

/**
 * <p>Description: 重试策略-不重试</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class NoRetryStrategy implements RetryStrategy{

    @Override
    public RpcResponse doRetry(Callable<RpcResponse> callable) throws Exception {
        return callable.call();
    }
}