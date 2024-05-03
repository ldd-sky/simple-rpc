package org.school.work.fault.tolerant;

import lombok.extern.slf4j.Slf4j;
import org.school.work.model.RpcResponse;

import java.util.Map;

/**
 * <p>Description: 容错策略-静默处理异常</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
@Slf4j
public class FailSafeTolerantStrategy implements TolerantStrategy{
    @Override
    public RpcResponse doTolerant(Map<String, Object> context, Exception e) {
        log.info("静默处理异常", e);
        return new RpcResponse();
    }
}