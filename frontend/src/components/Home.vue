<template>
    <v-container>
        <v-row>
            <v-col>
                <h1 class="title">游学景点或学校推荐</h1>
                <div class="filters">
                    <v-text-field v-model="searchQuery" label="搜索景点或学校" @input="fetchRecommendations"
                        clearable></v-text-field>
                    <div class="filter-group">
                        <h3>类别</h3>
                        <v-btn v-for="category in categoryOptions" :key="category" @click="toggleCategory(category)"
                            :class="{ 'selected-btn': selectedCategories.includes(category) }" class="filter-btn">
                            {{ category }}
                        </v-btn>
                    </div>
                    <div class="filter-group">
                        <h3>地区</h3>
                        <v-btn v-for="region in regionOptions" :key="region" @click="toggleRegion(region)"
                            :class="{ 'selected-btn': selectedRegions.includes(region) }" class="filter-btn">
                            {{ region }}
                        </v-btn>
                    </div>
                </div>
                <v-select v-model="sortBy" :items="sortOptions" label="排序方式"></v-select>
            </v-col>
        </v-row>
        <v-row>
            <v-col v-for="recommendation in recommendations" :key="recommendation.id" cols="12" md="4">
                <v-card @click="navigateToDetail(recommendation.id)">
                    <v-card-title>{{ recommendation.name }}</v-card-title>
                    <v-card-text>
                        <div class="description">{{ recommendation.description }}</div>
                        <div class="info-item"><v-icon left>mdi-fire</v-icon>热度: {{ recommendation.popularity }}</div>
                        <div class="info-item"><v-icon left>mdi-star</v-icon>评分: {{ (recommendation.rating * 100) }}
                        </div>
                        <div class="info-item"><v-icon left>mdi-currency-cny</v-icon>价格: {{ recommendation.price
                            }}<span>元</span></div>
                        <div class="info-item"><v-icon left>mdi-map-marker</v-icon>地址: {{ recommendation.address }}
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
export default {
    data() {
        return {
            recommendations: [],
            sortBy: '热度',
            selectedCategories: [],
            selectedRegions: [],
            searchQuery: ''
        };
    },
    computed: {
        sortOptions() {
            return ['热度', '评分', '价格'];
        },
        categoryOptions() {
            return ['5A景区', '4A景区', '3A景区', '学校'];
        },
        regionOptions() {
            return ['东城', '西城', '朝阳', '丰台', '石景山', '海淀', '门头沟', '房山', '大兴', '顺义', '昌平', '怀柔', '平谷', '密云', '延庆'];
        }
    },
    methods: {
        toggleCategory(category) {
            const index = this.selectedCategories.indexOf(category);
            if (index === -1) {
                this.selectedCategories.push(category);
            } else {
                this.selectedCategories.splice(index, 1);
            }
            this.fetchRecommendations();
        },
        toggleRegion(region) {
            const index = this.selectedRegions.indexOf(region);
            if (index === -1) {
                this.selectedRegions.push(region);
            } else {
                this.selectedRegions.splice(index, 1);
            }
            this.fetchRecommendations();
        },
        async fetchRecommendations() {
            const categories = this.selectedCategories.length > 0 ? this.selectedCategories.join(',') : 'all';
            const regions = this.selectedRegions.length > 0 ? this.selectedRegions.join(',') : 'all';
            const sortValue = this.sortBy;
            const query = this.searchQuery;
            try {
                const response = await fetch(`http://127.0.0.1:5000/recommendations?sortBy=${sortValue}&categories=${categories}&regions=${regions}&query=${query}`);
                const data = await response.json();
                this.recommendations = data;
            } catch (error) {
                console.error('Error fetching recommendations:', error);
            }
        },
        navigateToDetail(id) {
            this.$router.push(`/detail/${id}`);
        }
    },
    watch: {
        sortBy() {
            this.fetchRecommendations();
        }
    },
    created() {
        this.fetchRecommendations();
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

.filters {
    margin-bottom: 20px;
}

.filter-group {
    margin-bottom: 10px;
}

.filter-btn {
    margin-right: 10px;
    margin-bottom: 10px;
}

.selected-btn {
    background-color: #1976D2;
    color: white;
}

.info-item {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.info-item v-icon {
    margin-right: 8px;
}

.description {
    margin-bottom: 10px;
}
</style>