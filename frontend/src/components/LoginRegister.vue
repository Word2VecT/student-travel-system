<template>
    <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
            <v-col cols="12" md="8" lg="4">
                <div class="title-wrapper">
                    <h1>学生游学系统</h1>
                </div>
                <transition name="fade-slide" mode="out-in">
                    <div :key="isLogin" class="card-wrapper">
                        <v-card>
                            <v-card-title>
                                <span v-if="isLogin" class="text-h5">登录</span>
                                <span v-else class="text-h5">注册</span>
                            </v-card-title>
                            <v-card-text>
                                <v-form @submit.prevent="isLogin ? login() : register()">
                                    <v-text-field v-model="username" label="用户名" required></v-text-field>
                                    <v-text-field v-model="password" label="密码" type="password" required></v-text-field>
                                    <v-text-field v-if="!isLogin" v-model="confirmPassword" label="确认密码" type="password"
                                        required></v-text-field>
                                    <v-btn type="submit" color="primary">{{ isLogin ? '登录' : '注册' }}</v-btn>
                                </v-form>
                            </v-card-text>
                            <v-card-actions>
                                <v-btn text @click="toggleForm">{{ isLogin ? '需要注册？' : '已有账户？' }}</v-btn>
                            </v-card-actions>
                        </v-card>
                    </div>
                </transition>
                <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000" top right>
                    {{ snackbarMessage }}
                </v-snackbar>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
export default {
    data() {
        return {
            isLogin: true,
            username: '',
            password: '',
            confirmPassword: '',
            snackbar: false,
            snackbarMessage: '',
            snackbarColor: 'error',
        };
    },
    methods: {
        toggleForm() {
            this.isLogin = !this.isLogin;
            this.username = '';
            this.password = '';
            this.confirmPassword = '';
        },
        async login() {
            const response = await fetch('http://127.0.0.1:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: this.username,
                    password: this.password,
                }),
            });

            const data = await response.json();
            if (response.ok) {
                if (data.success) {
                    localStorage.setItem('username', this.username);
                    setTimeout(() => {
                        this.$router.push('/home');
                    }, 500); // 延迟 0.5 秒导航
                } else {
                    this.showSnackbar(data.message, 'error');
                }
            } else {
                this.showSnackbar('登录失败：' + (data.message || '服务器错误'), 'error');
            }
        },
        async register() {
            if (this.password !== this.confirmPassword) {
                this.showSnackbar('密码不匹配！', 'error');
                return;
            }

            const response = await fetch('http://127.0.0.1:5000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: this.username,
                    password: this.password,
                }),
            });

            const data = await response.json();
            if (response.ok) {
                if (data.success) {
                    this.showSnackbar(data.message, 'success');
                    setTimeout(() => {
                        this.isLogin = true; // 切换到登录视图
                    }, 500); // 延迟 0.5 秒切换视图
                } else {
                    this.showSnackbar(data.message, 'error');
                }
            } else {
                this.showSnackbar('注册失败：' + (data.message || '服务器错误'), 'error');
            }
        },
        showSnackbar(message, color) {
            this.snackbarMessage = message;
            this.snackbarColor = color;
            this.snackbar = true;
        },
    },
};
</script>


<style scoped>
.fill-height {
    height: 100vh;
    position: relative;
    overflow: hidden;
}

.title-wrapper {
    text-align: center;
    margin-bottom: 20px;
}

.card-wrapper {
    position: relative;
    z-index: 1;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
    transition: all 0.5s ease;
}

.fade-slide-enter,
.fade-slide-leave-to {
    transform: translateY(20px);
    opacity: 0;
}
</style>