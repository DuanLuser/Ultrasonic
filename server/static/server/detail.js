//全局设置参数 begin
DATA_UPDATE_INTERVAL = 3000;  //更新数据的时间间隔
//end

//全局变量 begin
UpdateDataTimer = undefined;          //更新数据的定时器句柄
LastOutcome = -1;
/**
 * 设置EChart的垂直线
 * @param {EChart} chart EChart
 * @param {number[]} dataArray 包含垂直线横坐标的数据 e.g. [1,2,3]
 */
function setChartLines(chart, dataArray) {
    let lines = [];
    for (let a of dataArray) {
        lines.push({ xAxis: a.EncoderAcum });
    }

    chart.setOption({
        series: [
            {
                markLine: {
                    data: lines
                },
            }
        ]
    });
}

/**
 * 设置EChart的数据集
 * @param {EChart} chart Echart实例
 * @param {any[]} dataArray 作为dataset的数组
 */
function setChartDataset(chart, dataArray) {
    chart.setOption({
        dataset: {
            source: dataArray,
        }
    });
}


/**
 * 初始化各个厚度图形
 * @param {HTMLElement} element 用以显示图形的div
 * @param {number} id 设备id
 */
function initChart(element, id) {
    let chart = echarts.init(element);
    //var data = [[5,0]];

    chart.setOption({
        title: {
            left: 'center',
            text: `检测图`,
            show: true
        },
	/*
        xAxis: {
            type: 'value', 
            axisLine: {
                onZero: false,
            },
            axisLabel: {
                interval:0,
            },
            name: '距离(m)',
            min: -3,
            max: 3,
        },
        yAxis: {
            type: 'value',
            scale: false,
            splitLine: {
                show: true,
                lineStyle: {
                
                }
            },
            name: `距离(m)`,
            min: 0,
            max: 3,
        },
        series: [{
            type: 'line',
            animationEasingUpdate: 'linear',
            markLine: {
                //silent: true,
                symbol: 'none',
                //animation: false,
                precision: 3,
                lineStyle: {
                    color: 'black',
                },
            },
        }],
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            },
            position: pt => [pt[0], '10%'],
        },*/
        polar: { show:true },
        /*tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },*/
        angleAxis: {
            max: 360,
            type: 'value',
            startAngle: 180,
            clockwise:true,
            minInterval:45,
            
        },
        radiusAxis: {
            max: 3,
        },
        series: [{ //暂定五个物体
            startAngle: 180,
            coordinateSystem: 'polar',
            //name: 'line',
            type: 'line',
	    show:false,
            //data: [[0,0],[0,0]],
        },{
            startAngle: 180,
            coordinateSystem: 'polar',
            type: 'line',
	    show:false,
        },{
            startAngle: 180,
            coordinateSystem: 'polar',
            type: 'line',
	    show:false,
        },{
            startAngle: 180,
            coordinateSystem: 'polar',
            type: 'line',
	    show:false,
        },{
            startAngle: 180,
            coordinateSystem: 'polar',
            type: 'line',
	    show:false,
        }],
        //animationDuration: 2000
    });

    return chart;
}


/**
 * 获取具体的测量表的ID并初始化界面各个图表
 */
function init() {
    const matches = document.URL.match(/device\/(\d+)/);
    deviceId = parseInt(matches[1]);
    console.log(deviceId);
    Charts = {};            //图形列表（字典）
    DataBuffer = {};        //数据缓冲区（字典）
    //检测表
    let element = document.createElement("div");
    element.className = "chart";
    //element.style.height=document.body.clientWidth+'px';
    document.getElementById("chart-wrapper").appendChild(element);
    Charts[deviceId] = initChart(element, deviceId);        //将该设备的图表加入到图形列表

    DataBuffer[deviceId] = [];  //初始化该设备的数据缓冲区
    let hostname = window.location.hostname;
    GetOutcomeUrl = `http://${hostname}:8000/api/device/?deviceid=${deviceId}`;
    startUpdateData();  //开始更新数据
}

function showInfo(msg) {
    let alerthtml = `
        <div class="alert alert-warning alert-dismissible fade show" role="alert">
            ${msg}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
            </button>
        </div>`
    document.getElementById("alert_wrapper").innerHTML = alerthtml;
}
function getOutcome() {

    $.get(GetOutcomeUrl, response => {
        //console.log(response);
        if (response.length > 0) {	
            if (response[0].device_status == 'online') {
                LastOutcome = 1;
                document.getElementById("status").innerText="检测中...";
                document.getElementById("obstacle").innerText="无相关参数";
            }
            else
                LastOutcome = -1;
        }
        //console.log(LastOutcome);
        if (LastOutcome != -1) {
            distance=response[0].distance;
            angle=response[0].angle;
            if (distance != "") {
                console.log(angle,distance);
                c = 0;
                obstacle_num=parseInt(angle.substring(angle.length-1,angle.length));
                var d = [0, 0, 0, 0, 0];
                var minAngle = [0, 0, 0, 0, 0];
                var maxAngle = [0, 0, 0, 0, 0];
                str = "";
                for(i=0; i< obstacle_num; i++) {
                    d[i] = parseFloat(distance.substring(i*5,4+i*5));
                    minAngle[i] = parseInt(angle.substring(i*8,3+i*8));
                    maxAngle[i] = parseInt(angle.substring(4+i*8,7+i*8));
                    str+="物体"+String(i+1)+" 角度："+String(minAngle[i])+"-"+String(maxAngle[i])+"°，距离："+String(d[i])+"m；";
                }
                document.getElementById("status").innerText="识别到新增障碍物";
                document.getElementById("obstacle").innerText= str;
		console.log(minAngle,maxAngle);
                if(angle=="左侧") c=45;
                else if(angle=="前方") c=90;
                else if(angle=="右侧") c=135;
                Charts[deviceId].setOption({
                	series: [{
            			data: [[d[0],minAngle[0]],[d[0],maxAngle[0]]]
                                //[[d-0.1,c-3],[d+0.1,c+3],[d,c],[d+0.1,c-3],[d-0.1,c+3]]
        		},
                        { data: [[d[1],minAngle[1]],[d[1],maxAngle[1]]] },
                        { data: [[d[2],minAngle[2]],[d[2],maxAngle[2]]] },
                        { data: [[d[3],minAngle[3]],[d[3],maxAngle[3]]] },
                        { data: [[d[4],minAngle[4]],[d[4],maxAngle[4]]] },
                        ],
                });
            }
            else if (distance == "") {
                document.getElementById("status").innerText="未识别到新增障碍物"; 
                document.getElementById("obstacle").innerText="无相关参数"; 
                Charts[deviceId].setOption({
                	series: [{
            			data: [[0,0],[0,0]]
        		},{data: [[0,0],[0,0]]},
                          {data: [[0,0],[0,0]]},
                          {data: [[0,0],[0,0]]},
                          {data: [[0,0],[0,0]]},
                        ],
                });
            }
            document.getElementById("alert_wrapper").innerHTML = null;
            
        } else  if (LastOutcome == -1){
            document.getElementById("status").innerText="未进行检测";
            document.getElementById("obstacle").innerText="无相关参数";
            showInfo("未检测到信号！设备未在线");
            Charts[deviceId].setOption({
                series: [{
            		data: [[0,0],[0,0]],
        	},{data: [[0,0],[0,0]]},
                {data: [[0,0],[0,0]]},
                {data: [[0,0],[0,0]]},
                {data: [[0,0],[0,0]]},
                ]
            });
        }
    });
   
}


/**
 * 开始更新数据
 */
function startUpdateData() {
    if (UpdateDataTimer == undefined) {
        getOutcome(); //立即更新一次，否则需要等一个interval
        UpdateDataTimer = setInterval(getOutcome, DATA_UPDATE_INTERVAL);
    }
}


/**
 * 停止更新数据
 */
function stopUpdateData() {
    if (UpdateDataTimer != undefined) {
        clearInterval(UpdateDataTimer);
        UpdateDataTimer = undefined;
        toastr.info("已停止更新数据！");
    }
}

/*
 * 页面可伸缩
 */
window.onresize = function () {
    for (let id in Charts) {
        Charts[id].resize();
    }
};

//开始更新数据
init();
