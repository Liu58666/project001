# Implementation Plan: Admin Task Publish

## Overview

实现管理端任务发布功能，包括任务服务层和发布页面组件。参考现有的 BroadcastMessage.vue 风格实现。

## Tasks

- [x] 1. 创建任务服务层
  - [x] 1.1 创建 src/services/taskService.js
    - 实现 createTask 函数
    - 使用 apiRequest 封装 POST /api/admin/tasks
    - 添加参数验证（content 必填，roles/user_ids 至少一个）
    - _Requirements: 4.3, 5.3_

- [x] 2. 创建任务发布页面组件
  - [x] 2.1 创建 src/pages/TaskPublish.vue 基础结构
    - 创建页面模板框架（header、form-section、bottom-bar）
    - 设置 script setup 和基础导入
    - 定义表单状态（form.title, form.content, form.roles）
    - 实现权限检查和页面进入动画
    - _Requirements: 5.1, 5.2_

  - [x] 2.2 实现表单输入区域
    - 添加标题输入框（maxlength: 200）
    - 添加内容文本域（maxlength: 5000）
    - 添加字符计数显示
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 2.3 实现角色选择功能
    - 添加角色选择芯片组件
    - 实现 toggleRole 函数
    - 添加选中状态样式
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 2.4 实现用户选择功能
    - 添加用户选择卡片按钮
    - 添加已选用户标签显示
    - 实现 removeUser 函数
    - _Requirements: 3.4, 3.5, 3.6_

  - [x] 2.5 实现用户选择弹窗
    - 添加弹窗模板（overlay、container、header、body、footer）
    - 实现搜索输入和过滤逻辑
    - 实现用户列表渲染和选择切换
    - 实现 loadUsers 函数调用 adminService
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 2.6 实现底部操作栏
    - 添加接收者统计显示
    - 添加返回按钮
    - 添加提交按钮
    - _Requirements: 4.4_

  - [x] 2.7 实现表单提交逻辑
    - 实现 handleSubmit 函数
    - 添加表单验证（content 非空、接收者非空）
    - 调用 taskService.createTask
    - 处理成功响应（显示消息、重置表单）
    - 处理错误响应（显示错误消息）
    - _Requirements: 4.1, 4.2, 4.3, 4.5, 4.6, 4.7, 4.8_

  - [x] 2.8 添加国际化文本
    - 添加所有中英文标签和提示
    - 使用 isZh 计算属性切换语言
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 3. 添加页面样式
  - [x] 3.1 添加 TaskPublish.vue 样式
    - 复用 BroadcastMessage.vue 的样式结构
    - 添加 reveal 动画样式
    - 添加表单、弹窗、底部栏样式
    - _Requirements: 1.1, 2.3, 3.1_

- [x] 4. 配置路由
  - [x] 4.1 在 router/index.js 中添加 /task-publish 路由
    - 导入 TaskPublish 组件
    - 配置路由路径和元信息
    - _Requirements: 5.1_

- [x] 5. Checkpoint - 功能验证
  - 确保所有代码无语法错误
  - 确保页面可以正常访问
  - 如有问题请询问用户

## Notes

- 样式参考 BroadcastMessage.vue，保持 UI 一致性
- 使用现有的 stores（error、success、user、i18n）
- 使用现有的 adminService.listAllUsers 获取用户列表
- 权限检查：role >= 3 可访问（Manager 和 Admin）
