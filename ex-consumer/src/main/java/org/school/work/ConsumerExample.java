package org.school.work;

import org.school.work.bootstrap.ConsumerBootstrap;
import org.school.work.model.User;
import org.school.work.proxy.ServiceProxyFactory;
import org.school.work.service.UserService;

/**
 * <p>Description: 简单的消费者示例</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年04月30日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class ConsumerExample {

    public static void main(String[] args) {
        // 服务提供者初始化
        ConsumerBootstrap.init();

        // 获取代理
        UserService userService = ServiceProxyFactory.getProxy(UserService.class);
        User user = new User();
        user.setName("testUserName");

        // 调用
        User newUser = userService.getUser(user);
        if(newUser != null){
            System.out.println(newUser.getName());
        } else {
            System.out.println("user is null");
        }
        long number = userService.getNumber();
        System.out.println(number);
    }
}