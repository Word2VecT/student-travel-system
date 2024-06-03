<template>
    <v-container>
        <h1 class="title">{{ destination.name }}</h1>
        <v-card class="info-card">
            <v-card-text>
                <div class="info-container">
                    <div class="info-details">
                        <div class="info-item">热度: {{ destination.popularity }}</div>
                        <div class="info-item">评分: {{ (destination.rating * 100).toFixed(2) }}</div>
                        <div class="info-item">价格: {{ destination.price }}<span>元</span></div>
                        <div class="info-item">地址: {{ destination.address }}</div>
                        <div class="description">{{ destination.description }}</div>
                    </div>
                    <div class="map-container">
                        <v-btn @click="navigateToTravel" class="map-btn" icon>
                            <v-icon size="48" class="center-icon">mdi-map-marker</v-icon>
                        </v-btn>
                        <div class="map-text">开始游学</div>
                    </div>
                </div>
            </v-card-text>
        </v-card>

        <v-btn @click="navigateToHome" class="back-btn" icon>
            <v-icon>mdi-arrow-left</v-icon>
        </v-btn>

        <h2 class="sub-title">浏览游记</h2>
        <v-text-field v-model="searchQuery" label="搜索游记" clearable @input="fetchTravelNotes"></v-text-field>
        <v-select v-model="sortBy" :items="sortOptions" label="排序方式" class="sort-select"
            @change="fetchTravelNotes"></v-select>
        <div class="notes-container">
            <v-row>
                <v-col v-if="travelNotes.length === 0" cols="12">
                    <p class="no-notes">还没有游记，快来写一篇吧！</p>
                </v-col>
                <v-col v-else v-for="note in travelNotes" :key="note.id" cols="12" md="6">
                    <v-card class="note-card">
                        <v-card-title>
                            <div>{{ note.title }}</div>
                            <span class="author">by {{ note.username }}</span>
                            <v-btn icon @click="toggleFullNote(note)" class="toggle-button">
                                <v-icon>{{ note.showFull ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
                            </v-btn>
                        </v-card-title>
                        <v-divider :style="{ 'border-color': '#BBBBBB' }"></v-divider>
                        <v-card-text>
                            <div class="info-row">
                                <div class="info-item">浏览量: {{ note.views }}</div>
                                <div class="info-item">评分: {{ note.rating.toFixed(2) }}</div>
                            </div>
                            <div v-html="note.content" class="note-content" :class="{ 'full-note': note.showFull }">
                            </div>
                            <v-divider v-if="note.showFull" :style="{ 'border-color': '#BBBBBB' }"></v-divider>
                            <div v-if="note.showFull" class="rate-section">
                                <div class="rate-text">为该游记评分</div>
                                <v-rating v-model="note.newRating" half-increments hover @click="submitRating(note)"
                                    :length="5" color="black" background-color="grey lighten-1"
                                    empty-icon="mdi-star-outline" half-icon="mdi-star-half-full" full-icon="mdi-star" />
                            </div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </div>

        <h2 class="sub-title">写游记</h2>
        <v-card class="editor-card">
            <v-card-text>
                <v-text-field v-model="noteTitle" label="文章名称" required></v-text-field>
                <div style="border: 1px solid #ccc; margin-top: 10px;">
                    <Toolbar :editor="editorRef" :defaultConfig="toolbarConfig" :mode="mode"
                        style="border-bottom: 1px solid #ccc" />
                    <Editor :defaultConfig="editorConfig" :mode="mode" v-model="valueHtml"
                        style="height: 400px; overflow-y: hidden;" @onCreated="handleCreated" @onChange="handleChange"
                        @onDestroyed="handleDestroyed" @onFocus="handleFocus" @onBlur="handleBlur"
                        @customAlert="customAlert" @customPaste="customPaste" />
                </div>
                <v-btn color="primary" @click="submitTravelNote" class="submit-btn">发布游记</v-btn>
            </v-card-text>
        </v-card>
    </v-container>
</template>

<script>
import '@wangeditor/editor/dist/css/style.css';
import { onBeforeUnmount, ref, shallowRef, onMounted } from 'vue';
import { Editor, Toolbar } from '@wangeditor/editor-for-vue';
import { VRating } from 'vuetify/components/VRating';

export default {
    components: { Editor, Toolbar, VRating },
    setup() {
        const editorRef = shallowRef(null);
        const valueHtml = ref('');
        const toolbarConfig = {};
        const editorConfig = {
            placeholder: '请输入游记内容...',
            MENU_CONF: {
                uploadImage: {
                    fieldName: 'uploadedImage',
                    maxFileSize: 10 * 1024 * 1024, // 10M
                    maxNumberOfFiles: 10,
                    allowedFileTypes: ['image/*'],

                    meta: { token: 'xxx', a: 100 },
                    metaWithUrl: true, // 参数拼接到 url 上
                    headers: { Accept: 'text/x-json' },

                    timeout: 5 * 1000, // 5 秒
                    server: 'http://127.0.0.1:5000/upload', // 上传图片的服务器地址
                    onBeforeUpload(file) {
                        console.log('onBeforeUpload', file);
                        return file;
                    },
                    onProgress(progress) {
                        console.log('onProgress', progress);
                    },
                    onSuccess(file, res) {
                        console.log('onSuccess', file, res);
                        if (res.errno === 0) {
                            // 将图片 URL 插入编辑器
                            const imageUrl = res.data.url;
                            editorRef.value.insertImage(imageUrl, '', '');
                        } else {
                            alert('上传失败');
                        }
                    },
                    onFailed(file, res) {
                        console.log('onFailed', file, res);
                        alert(`${file.name} 上传失败`);
                    },
                    onError(file, err, res) {
                        console.log('onError', file, err, res);
                        alert(`${file.name} 上传出错`);
                    },
                }
            }
        };

        onMounted(() => {
            setTimeout(() => {
                valueHtml.value = '';
            }, 1500);
        });

        onBeforeUnmount(() => {
            const editor = editorRef.value;
            if (editor) {
                editor.destroy();
            }
        });

        const handleCreated = (editor) => {
            editorRef.value = editor;
        };
        const handleChange = (editor) => {
            valueHtml.value = editor.getHtml();
        };
        const handleDestroyed = (editor) => {
            console.log('destroyed', editor);
        };
        const handleFocus = (editor) => {
            console.log('focus', editor);
        };
        const handleBlur = (editor) => {
            console.log('blur', editor);
        };
        const customAlert = (info, type) => {
            alert(`【自定义提示】${type} - ${info}`);
        };
        const customPaste = (editor, event, callback) => {
            console.log('ClipboardEvent 粘贴事件对象', event);
            editor.insertText('xxx');
            callback(false);
        };

        const insertText = () => {
            const editor = editorRef.value;
            if (editor == null) return;
            editor.insertText('hello world');
        };

        const printHtml = () => {
            const editor = editorRef.value;
            if (editor == null) return;
            console.log(editor.getHtml());
        };

        const disable = () => {
            const editor = editorRef.value;
            if (editor == null) return;
            editor.disable();
        };

        return {
            editorRef,
            mode: 'default',
            valueHtml,
            toolbarConfig,
            editorConfig,
            handleCreated,
            handleChange,
            handleDestroyed,
            handleFocus,
            handleBlur,
            customAlert,
            customPaste,
            insertText,
            printHtml,
            disable,
        };
    },
    data() {
        return {
            destination: {},
            travelNotes: [],
            noteTitle: '',
            sortBy: '浏览量',
            searchQuery: ''
        };
    },
    computed: {
        sortOptions() {
            return ['浏览量', '评分'];
        },
    },
    methods: {
        fetchDestination() {
            const id = this.$route.params.id;
            fetch(`http://127.0.0.1:5000/destination/${id}`)
                .then(response => response.json())
                .then(data => {
                    this.destination = data;
                });
        },
        async fetchTravelNotes() {
            const id = this.$route.params.id;
            const sortBy = this.sortBy;
            const searchQuery = this.searchQuery;
            const response = await fetch(`http://127.0.0.1:5000/destination/${id}/notes?sortBy=${sortBy}&searchQuery=${searchQuery}`);
            const data = await response.json();
            this.travelNotes = data.map(note => ({ ...note, showFull: false, newRating: 0 }));
        },
        toggleFullNote(note) {
            note.showFull = !note.showFull;
            if (note.showFull) {
                this.incrementViews(note.id);
            }
        },
        incrementViews(noteId) {
            fetch(`http://127.0.0.1:5000/note/${noteId}/increment_views`, {
                method: 'POST'
            }).then(() => {
                const note = this.travelNotes.find(note => note.id === noteId);
                if (note) {
                    note.views += 1;
                }
            });
        },
        submitRating(note) {
            fetch(`http://127.0.0.1:5000/note/${note.id}/rate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rating: note.newRating * 20 })  // 将星级转换为百分比
            }).then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.fetchTravelNotes();
                    } else {
                        alert(data.message);
                    }
                });
        },
        submitTravelNote() {
            const id = this.$route.params.id;
            const username = localStorage.getItem('username');
            fetch(`http://127.0.0.1:5000/destination/${id}/notes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: this.noteTitle, content: this.valueHtml, username })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.fetchTravelNotes();
                        this.noteTitle = '';
                        this.valueHtml = '';
                    } else {
                        alert(data.message);
                    }
                });
        },
        navigateToHome() {
            this.$router.push('/home');
        },
        navigateToTravel() {
            const id = this.$route.params.id;
            this.$router.push(`/travel/${id}`);
        },
    },
    watch: {
        sortBy() {
            this.fetchTravelNotes();
        },
        searchQuery() {
            this.fetchTravelNotes();
        }
    },
    created() {
        this.fetchDestination();
        this.fetchTravelNotes();
    }
};
</script>

<style scoped>
.v-container {
    padding-top: 20px;
}

.title {
    text-align: center;
    margin-bottom: 20px;
}

.info-card,
.note-card,
.editor-card {
    margin-bottom: 20px;
}

.info-item {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.description {
    margin-bottom: 10px;
}

.note-title {
    font-weight: bold;
    margin-bottom: 8px;
}

.author {
    color: #888;
    margin-left: auto;
}

.sub-title {
    margin-top: 20px;
    margin-bottom: 10px;
}

.no-notes {
    color: #888;
    text-align: center;
    font-size: 16px;
}

.note-content {
    overflow: hidden;
    max-height: 80px;
    text-overflow: ellipsis;
}

.full-note {
    max-height: none;
}

.info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.rate-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 16px;
}

.rate-text {
    margin-bottom: 4px;
    text-align: center;
}

.toggle-button {
    position: absolute;
    top: 8px;
    right: 8px;
    background-color: #fff;
    border-radius: 50%;
}

.v-divider {
    margin-top: 8px;
    margin-bottom: 8px;
    border-color: #BBBBBB;
}

.notes-container {
    max-height: 400px;
    overflow-y: auto;
    overflow-x: hidden;
}

.submit-btn {
    margin-left: 10px;
    margin-top: 10px;
}

.sort-select {
    margin-bottom: 10px;
}

.back-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #1976D2;
    color: white;
    border-radius: 50%;
}

.info-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.info-details {
    flex-grow: 1;
}

.map-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-left: 20px;
}

.map-btn {
    margin-right: 50px;
    background-color: #1976D2;
    color: white;
    width: 90px;
    height: 90px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 50%;
}

.map-text {
    color: #1976D2;
    font-weight: bold;
    margin-right: 50px;
    margin-top: 8px;
    font-size: 20px;
    text-align: center;
}

.center-icon {
    margin: 0;
}
</style>