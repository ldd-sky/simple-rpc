package org.school.work.service;

import org.school.work.model.User;

/**
 * <p>Description: 用户服务</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年04月30日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public interface UserService {
    /**
     * 获取用户
     * @param user  用户
     * @return      用户
     */
    User getUser(User user);
}