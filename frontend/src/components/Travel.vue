<template>
    <div>
        <div id="searchContainer">
            <input
                v-model="searchQuery"
                id="tipinput"
                placeholder="请输入关键字"
            />
            <div id="panel"></div>
        </div>
        <v-btn @click="toggleRoutePlanning" class="route-btn" icon>
            <v-icon>{{
                routePlanningEnabled ? "mdi-close" : "mdi-map-marker-path"
            }}</v-icon>
        </v-btn>
        <v-btn @click="toggleMultiPointMode" class="multi-point-btn" icon>
            <v-icon>{{
                multiPointModeEnabled ? "mdi-close" : "mdi-map-marker-multiple"
            }}</v-icon>
        </v-btn>
        <v-btn
            v-if="multiPointModeEnabled"
            @click="toggleCostMode"
            class="cost-mode-btn"
            icon
        >
            <v-icon>{{
                useTimeAsCost ? "mdi-clock" : "mdi-road-variant"
            }}</v-icon>
        </v-btn>
        <v-btn
            v-if="multiPointModeEnabled"
            @click="endMultiPointSelection"
            class="end-selection-btn"
            icon
        >
            <v-icon>mdi-check</v-icon>
        </v-btn>
        <v-btn @click="toggleRouteMode" class="mode-btn" icon>
            <v-icon>{{ isBikingMode ? "mdi-bike" : "mdi-walk" }}</v-icon>
        </v-btn>
        <v-btn @click="clearAllRoutes" class="clear-btn" icon>
            <v-icon>mdi-delete</v-icon>
        </v-btn>
        <v-btn @click="navigateToDetail" class="back-btn" icon>
            <v-icon>mdi-arrow-left</v-icon>
        </v-btn>
        <v-snackbar v-model="snackbar" :timeout="snackbarTimeout" top right>
            <div class="snackbar-message">{{ snackbarMessage }}</div>
        </v-snackbar>
        <v-card v-if="shortestRouteInfo.length" class="route-info-card">
            <v-card-title>路径信息</v-card-title>
            <v-divider></v-divider>
            <v-list dense>
                <v-list-item
                    v-for="(step, index) in shortestRouteInfo"
                    :key="index"
                >
                    <v-list-item-icon>
                        <v-icon>{{ getDirectionIcon(step.direction) }}</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>{{
                        step.instruction
                    }}</v-list-item-content>
                    <v-divider
                        v-if="step.isWaypoint"
                        class="waypoint-divider"
                    ></v-divider>
                </v-list-item>
            </v-list>
        </v-card>
        <div id="container"></div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import AMapLoader from "@amap/amap-jsapi-loader";

const searchQuery = ref("");
let map = null;
let walking = null;
let riding = null;
let startMarker = null;
let endMarker = null;
const waypoints = ref([]);
const routePlanningEnabled = ref(false);
const multiPointModeEnabled = ref(false);
const isBikingMode = ref(false);
const useTimeAsCost = ref(false);
const route = useRoute();
const router = useRouter();
const snackbar = ref(false);
const snackbarMessage = ref("");
const snackbarTimeout = ref(3000);
let polylines = [];
const shortestRouteInfo = ref([]);

const directionIcons = {
    左转: "mdi-arrow-left",
    右转: "mdi-arrow-right",
    stop: "mdi-arrow-up",
    向左前方行走: "mdi-arrow-top-left",
    向右前方行走: "mdi-arrow-top-right",
};

const getDirectionIcon = (direction) => {
    return directionIcons[direction] || "mdi-arrow-up";
};

const toggleRoutePlanning = () => {
    if (multiPointModeEnabled.value) {
        showSnackbar("请先关闭多点路径规划");
        return;
    }
    routePlanningEnabled.value = !routePlanningEnabled.value;
    if (routePlanningEnabled.value) {
        showSnackbar("导航模式已开启，再次点击以退出导航模式");
    } else {
        resetMarkersAndRoute();
        showSnackbar("导航模式已关闭");
    }
};

const toggleMultiPointMode = () => {
    if (routePlanningEnabled.value) {
        showSnackbar("请先关闭导航模式");
        return;
    }
    multiPointModeEnabled.value = !multiPointModeEnabled.value;
    if (multiPointModeEnabled.value) {
        showSnackbar("多点路径规划模式已开启，点击地图以添加点");
    } else {
        calculateAndDrawShortestRoute();
        showSnackbar("多点路径规划模式已关闭");
    }
};

const toggleRouteMode = () => {
    isBikingMode.value = !isBikingMode.value;
    showSnackbar(isBikingMode.value ? "切换到骑行模式" : "切换到步行模式");
};

const toggleCostMode = () => {
    useTimeAsCost.value = !useTimeAsCost.value;
    showSnackbar(useTimeAsCost.value ? "按时间计算" : "按路径计算");
};

const endMultiPointSelection = () => {
    calculateAndDrawShortestRoute();
    showSnackbar("多点路径规划完成");
};

const clearAllRoutes = () => {
    resetMarkersAndRoute();
    clearPolylines();
    shortestRouteInfo.value = [];
    showSnackbar("所有路径已清除");
};

const showSnackbar = (message) => {
    snackbarMessage.value = message;
    snackbar.value = true;
};

const resetMarkersAndRoute = () => {
    if (startMarker) {
        startMarker.setMap(null);
        startMarker = null;
    }
    waypoints.value.forEach((marker) => {
        marker.setMap(null);
    });
    waypoints.value = [];
    if (endMarker) {
        endMarker.setMap(null);
        endMarker = null;
    }
    if (walking) {
        walking.clear();
    }
    if (riding) {
        riding.clear();
    }
};

const clearPolylines = () => {
    polylines.forEach((polyline) => {
        polyline.setMap(null);
    });
    polylines = [];
};

const addWaypointMarker = (lng, lat) => {
    const waypointMarker = new AMap.Marker({
        position: [lng, lat],
        map: map,
        icon: "https://webapi.amap.com/theme/v2.0/markers/n/mid.png",
    });
    waypoints.value.push(waypointMarker);
};

const calculateAndDrawShortestRoute = () => {
    if (waypoints.value.length < 1) return;
    const points = [
        startMarker.getPosition(),
        ...waypoints.value.map((marker) => marker.getPosition()),
    ];
    const distances = [];
    const times = [];

    const promises = [];
    let n = points.length;
    for (let i = 0; i < n; i++) {
        distances[i] = [];
        times[i] = [];
        for (let j = 0; j < n; j++) {
            if (i !== j) {
                const origin = `${points[i].lng},${points[i].lat}`;
                const destination = `${points[j].lng},${points[j].lat}`;
                const url = isBikingMode.value
                    ? `https://restapi.amap.com/v4/direction/bicycling?origin=${origin}&destination=${destination}&key=05813388ef9a5c554ea0b78b411f9cd8`
                    : `https://restapi.amap.com/v3/direction/walking?origin=${origin}&destination=${destination}&key=05813388ef9a5c554ea0b78b411f9cd8`;
                promises.push(
                    fetch(url)
                        .then((response) => response.json())
                        .then((data) => {
                            if (data.status === "1" || data.errcode === 0) {
                                const route = data.route || data.data;
                                const distance = route.paths[0].distance;
                                const time = route.paths[0].duration;
                                distances[i][j] = distance;
                                times[i][j] = time;
                            } else {
                                throw new Error("Failed to fetch route data");
                            }
                        }),
                );
            } else {
                distances[i][j] = 0;
                times[i][j] = 0;
            }
        }
    }

    Promise.all(promises)
        .then(() => {
            const costMatrix = useTimeAsCost.value ? times : distances;

            // 将数据发送到后端计算最短路径
            fetch("http://127.0.0.1:5000/calculate-route", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    length: n,
                    cost: costMatrix,
                }),
            })
                .then((response) => response.json())
                .then((data) => {
                    const shortestRoute = data.path;
                    const path = shortestRoute.map((index) => points[index]);
                    console.log("Shortest route:", shortestRoute);
                    drawRoute(path, shortestRoute);
                })
                .catch((error) => {
                    console.error("Failed to calculate shortest route:", error);
                });
        })
        .catch((error) => {
            console.error("Failed to calculate shortest route:", error);
        });
};

const drawRoute = (path, shortestRoute) => {
    const fetchRouteUrl = (start, end) => {
        return isBikingMode.value
            ? `https://restapi.amap.com/v4/direction/bicycling?origin=${start}&destination=${end}&key=05813388ef9a5c554ea0b78b411f9cd8`
            : `https://restapi.amap.com/v3/direction/walking?origin=${start}&destination=${end}&key=05813388ef9a5c554ea0b78b411f9cd8`;
    };

    const routePromises = [];
    for (let i = 0; i < path.length - 1; i++) {
        routePromises.push(
            fetch(
                fetchRouteUrl(
                    `${path[i].lng},${path[i].lat}`,
                    `${path[i + 1].lng},${path[i + 1].lat}`,
                ),
            ).then((response) => response.json()),
        );
    }

    Promise.all(routePromises)
        .then((responses) => {
            shortestRouteInfo.value = [];
            responses.forEach((data, index) => {
                if (data.status === "1" || data.errcode === 0) {
                    const route = data.route || data.data;
                    const steps = route.paths[0].steps;
                    steps.forEach((step) => {
                        shortestRouteInfo.value.push({
                            instruction: step.instruction,
                            direction: step.action,
                            isWaypoint: false,
                        });
                    });

                    if (index < responses.length - 1) {
                        shortestRouteInfo.value.push({
                            instruction: "到达途径点",
                            direction: "stop",
                            isWaypoint: true,
                        });
                    }

                    const polylinePath = steps.flatMap((step) =>
                        step.polyline
                            .split(";")
                            .map((point) => point.split(",").map(Number)),
                    );
                    const polyline = new AMap.Polyline({
                        path: polylinePath,
                        isOutline: true,
                        outlineColor: "#ffeeee",
                        borderWeight: 2,
                        strokeWeight: 5,
                        strokeColor: "#0091ff",
                        strokeOpacity: 0.9,
                        lineJoin: "round",
                    });
                    map.add(polyline);
                    polylines.push(polyline);
                } else {
                    throw new Error("Failed to fetch route data");
                }
            });

            // 更新途经点标记
            waypoints.value.forEach((marker, index) => {
                const markerContent = `
                <div class="custom-marker">
                    <div>${index + 1}</div>
                </div>
            `;
                marker.setContent(markerContent);
            });
        })
        .catch((error) => {
            console.error("Failed to draw route:", error);
        });
};

const navigateToDetail = () => {
    const id = route.params.id;
    router.push(`/detail/${id}`);
};

onMounted(() => {
    const id = route.params.id;
    fetch(`http://127.0.0.1:5000/destination/${id}`)
        .then((response) => response.json())
        .then((data) => {
            const address = data.address;
            const apiKey = "05813388ef9a5c554ea0b78b411f9cd8";
            const geocodeUrl = `https://restapi.amap.com/v3/geocode/geo?address=${encodeURIComponent(
                address,
            )}&output=JSON&key=${apiKey}`;

            fetch(geocodeUrl)
                .then((response) => response.json())
                .then((geoData) => {
                    if (geoData.status === "1" && geoData.geocodes.length > 0) {
                        const location =
                            geoData.geocodes[0].location.split(",");
                        const longitude = parseFloat(location[0]);
                        const latitude = parseFloat(location[1]);

                        window._AMapSecurityConfig = {
                            securityJsCode: "5f93bea3c2041b19fc9f63eab05d1928",
                        };
                        AMapLoader.load({
                            key: "bbcd352c3dd337fe6291eb1d5e1eecdf",
                            version: "2.0",
                            plugins: [
                                "AMap.Scale",
                                "AMap.ToolBar",
                                "AMap.ControlBar",
                                "AMap.AutoComplete",
                                "AMap.PlaceSearch",
                                "AMap.Walking",
                                "AMap.Riding",
                            ],
                        })
                            .then((AMap) => {
                                map = new AMap.Map("container", {
                                    viewMode: "3D",
                                    zoom: 17,
                                    center: [longitude, latitude],
                                });

                                const scale = new AMap.Scale({
                                    position: "LB", // 左下角
                                });
                                const toolBar = new AMap.ToolBar({
                                    position: {
                                        top: "110px",
                                        right: "40px",
                                    },
                                });
                                const controlBar = new AMap.ControlBar({
                                    position: {
                                        top: "10px",
                                        right: "10px",
                                    },
                                });

                                map.addControl(scale);
                                map.addControl(toolBar);
                                map.addControl(controlBar);

                                const autoOptions = {
                                    input: "tipinput",
                                };
                                const autoComplete = new AMap.AutoComplete(
                                    autoOptions,
                                );
                                const placeSearch = new AMap.PlaceSearch({
                                    map: map,
                                    panel: "panel",
                                    autoFitView: true,
                                });

                                autoComplete.on("select", (e) => {
                                    placeSearch.setCity(e.poi.adcode);
                                    placeSearch.search(e.poi.name);
                                });

                                // 周边搜索
                                placeSearch.searchNearBy(
                                    "",
                                    [longitude, latitude],
                                    200,
                                    (status, result) => {
                                        console.log(status, result);
                                    },
                                );

                                // Initialize walking and biking navigation
                                walking = new AMap.Walking({
                                    map: map,
                                    panel: "panel",
                                    hideMarkers: true,
                                });

                                riding = new AMap.Riding({
                                    map: map,
                                    panel: "panel",
                                    hideMarkers: true,
                                });

                                // Handle map click to get coordinates
                                map.on("click", (e) => {
                                    if (
                                        !routePlanningEnabled.value &&
                                        !multiPointModeEnabled.value
                                    )
                                        return;
                                    const { lng, lat } = e.lnglat;

                                    if (multiPointModeEnabled.value) {
                                        if (!startMarker) {
                                            startMarker = new AMap.Marker({
                                                position: [lng, lat],
                                                map: map,
                                                icon: "https://webapi.amap.com/theme/v2.0/markers/n/start.png",
                                            });
                                        } else {
                                            addWaypointMarker(lng, lat);
                                        }
                                    } else {
                                        if (!startMarker) {
                                            startMarker = new AMap.Marker({
                                                position: [lng, lat],
                                                map: map,
                                                icon: "https://webapi.amap.com/theme/v2.0/markers/n/start.png",
                                            });
                                        } else if (!endMarker) {
                                            endMarker = new AMap.Marker({
                                                position: [lng, lat],
                                                map: map,
                                                icon: "https://webapi.amap.com/theme/v2.0/markers/n/end.png",
                                            });

                                            // Draw route
                                            if (isBikingMode.value) {
                                                riding.search(
                                                    startMarker.getPosition(),
                                                    endMarker.getPosition(),
                                                    (status, result) => {
                                                        if (
                                                            status ===
                                                            "complete"
                                                        ) {
                                                            showSnackbar(
                                                                "骑行路线规划完成",
                                                            );
                                                        } else {
                                                            showSnackbar(
                                                                "骑行路线规划失败",
                                                            );
                                                        }
                                                    },
                                                );
                                            } else {
                                                walking.search(
                                                    startMarker.getPosition(),
                                                    endMarker.getPosition(),
                                                    (status, result) => {
                                                        if (
                                                            status ===
                                                            "complete"
                                                        ) {
                                                            showSnackbar(
                                                                "步行路线规划完成",
                                                            );
                                                        } else {
                                                            showSnackbar(
                                                                "步行路线规划失败",
                                                            );
                                                        }
                                                    },
                                                );
                                            }
                                        } else {
                                            resetMarkersAndRoute();
                                        }
                                    }
                                });
                            })
                            .catch((e) => {
                                console.log(e);
                            });
                    }
                });
        });
});

onUnmounted(() => {
    map?.destroy();
});
</script>

<style scoped>
#container {
    width: 100%;
    height: 800px;
}

#searchContainer {
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 10;
    background: white;
    padding: 10px;
    border-radius: 5px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border: 2px solid #1976d2;
}

#tipinput {
    width: 250px;
    height: 30px;
    padding: 5px;
    border: 1px solid #1976d2;
    border-radius: 5px;
    outline: none;
}

#panel {
    margin-top: 10px;
    width: 250px;
    max-height: 300px;
    overflow-y: auto;
    background-color: white;
    border: 1px solid #1976d2;
    border-radius: 5px;
}

.route-btn {
    position: absolute;
    bottom: 70px;
    right: 20px;
    z-index: 10;
    background: #1976d2;
    color: white;
    padding: 10px;
    border-radius: 50%;
}

.mode-btn {
    position: absolute;
    bottom: 130px;
    right: 20px;
    z-index: 10;
    background: #1976d2;
    color: white;
    padding: 10px;
    border-radius: 50%;
}

.multi-point-btn {
    position: absolute;
    bottom: 190px;
    right: 20px;
    z-index: 10;
    background: #1976d2;
    color: white;
    padding: 10px;
    border-radius: 50%;
}

.cost-mode-btn {
    position: absolute;
    bottom: 250px;
    right: 20px;
    z-index: 10;
    background: #1976d2;
    color: white;
    padding: 10px;
    border-radius: 50%;
}

.end-selection-btn {
    position: absolute;
    bottom: 310px;
    right: 20px;
    z-index: 10;
    background: #1976d2;
    color: white;
    padding: 10px;
    border-radius: 50%;
}

.clear-btn {
    position: absolute;
    bottom: 370px;
    right: 20px;
    z-index: 10;
    background: #f44336;
    color: white;
    padding: 10px;
    border-radius: 50%;
}

.back-btn {
    position: absolute;
    bottom: 430px;
    right: 20px;
    z-index: 10;
    background: #1976d2;
    color: white;
    padding: 10px;
    border-radius: 50%;
}

.custom-marker {
    background-color: #1976d2;
    color: white;
    border-radius: 50%;
    width: 30px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: bold;
    line-height: 42px;
    text-align: center;
}

.snackbar-message {
    text-align: center;
    width: 100%;
}

.route-info-card {
    position: absolute;
    bottom: 20px;
    left: 20px;
    width: 300px;
    max-height: 400px;
    overflow-y: auto;
    z-index: 20;
}

.waypoint-divider {
    border-top: 1px solid #ccc;
    margin: 5px 0;
}
</style>
