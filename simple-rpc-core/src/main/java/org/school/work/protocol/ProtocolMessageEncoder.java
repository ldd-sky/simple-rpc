package org.school.work.protocol;

import io.vertx.core.buffer.Buffer;
import org.school.work.serializer.Serializer;
import org.school.work.serializer.SerializerFactory;

import java.io.IOException;

/**
 * <p>Description: 编码器</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class ProtocolMessageEncoder {

    /**
     * 编码
     */
    public static Buffer encode(ProtocolMessage<?> protocolMessage) throws IOException{
        if (protocolMessage == null || protocolMessage.getHeader() == null){
            return Buffer.buffer();
        }
        ProtocolMessage.Header header = protocolMessage.getHeader();
        // 一次向缓冲区写入字节
        Buffer buffer = Buffer.buffer();
        buffer.appendByte(header.getMagic());
        buffer.appendByte(header.getVersion());
        buffer.appendByte(header.getSerializer());
        buffer.appendByte(header.getType());
        buffer.appendByte(header.getStatus());
        buffer.appendLong(header.getRequestId());
        // 获取序列化器
        ProtocolMessageSerializerEnum serializerEnum = ProtocolMessageSerializerEnum.getEnumByKey(header.getSerializer());
        if (serializerEnum == null) {
            throw new RuntimeException("序列化协议不存在");
        }
        Serializer serializer = SerializerFactory.getInstance(serializerEnum.getValue());
        byte[] bodyBytes = serializer.serialize(protocolMessage.getBody());
        // 写入 body 长度和数据
        buffer.appendInt(bodyBytes.length);
        buffer.appendBytes(bodyBytes);
        return buffer;
    }
}