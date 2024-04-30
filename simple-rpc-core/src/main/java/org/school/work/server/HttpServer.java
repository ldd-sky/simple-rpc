package org.school.work.server;

/**
 * <p>Description: HTTP 服务器借口</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年04月30日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public interface HttpServer {
    /**
     * 启动服务器
     * @param port 端口
     */
    void doStart(int port);
}