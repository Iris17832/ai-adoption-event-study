# GitHub 远程仓库建立指引（张锦悦操作，约 10 分钟）

> 本机 SSH 密钥已由 Research Brain 生成完毕，你只需在浏览器完成 3 步，最后告诉我你的 GitHub 用户名，我来推送。

## 第 1 步：登录/注册 GitHub（2 分钟）

- 打开 https://github.com
- 已有账号直接登录；没有就点 Sign up 注册（邮箱+密码即可）

## 第 2 步：添加 SSH 公钥（3 分钟）

1. 点击右上角头像 → **Settings** → 左侧栏最下方 **SSH and GPG keys**
2. 点 **New SSH key**
3. Title 随便填（如 `MacBook-research`），Key type 保持 `Authentication Key`
4. 把下面这段公钥**完整复制**粘贴到 Key 框，点 **Add SSH key**：

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDZh4vrT4NgnfHmN95QSjKokaVI4p0yf7fx3xc7OBYAg zhangjinyue-sdufe-research
```

## 第 3 步：创建空仓库（2 分钟）

1. 点右上角 **+** → **New repository**
2. Repository name 填：`ai-adoption-event-study`（或你喜欢的名字）
3. 选择 **Public**（组委会检查点需要访问 Git 地址；仓库内只有代码和文档，不含原始数据和密钥）
4. **不要勾选** "Add a README file" 等任何初始化选项（保持空仓库）
5. 点 **Create repository**

## 第 4 步：告诉 Research Brain

回到对话里说一句"仓库建好了，我的用户名是 XXX"，我立即执行推送：

```
git remote add origin git@github.com:你的用户名/ai-adoption-event-study.git
git push -u origin master
```

推送完成后，仓库地址（填官网过程检查点"Git 地址"栏）：
`https://github.com/你的用户名/ai-adoption-event-study`

## 安全说明（已核验）

- `.env`（含 GLM API Key）在 .gitignore 中，**不会**推送到 GitHub
- 3,461 份年报 PDF、行情 CSV 等大数据文件均在 .gitignore 中，仓库仅含代码+文档+结果表（约 2 MB）
- git 提交身份已设置为「张锦悦 <zhangjinyue@users.noreply.github.com>」（GitHub 隐私保护邮箱格式，不暴露真实邮箱）
