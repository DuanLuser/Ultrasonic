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
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
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
        series: [{
            startAngle: 180,
            coordinateSystem: 'polar',
            //name: 'line',
            type: 'line',
	    show:false,
            data: [[0,0],[0,0]],
            
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
                document.getElementById("distance").innerText="检测中...";
                document.getElementById("angle").innerText="检测中...";
            }
            else
                LastOutcome = -1;
        }
        //console.log(LastOutcome);
        if (LastOutcome != -1) {
            distance=response[0].distance;
            angle=response[0].angle;
            if (distance != '' && distance != '0.00m') {
                console.log(angle,distance);
                c=0;
                d=parseFloat(distance.substring(0,4));
		minAngle=parseInt(angle.substring(0,3));
                maxAngle=parseInt(angle.substring(4,7));
                document.getElementById("distance").innerText="距离监测点 "+distance;
		document.getElementById("angle").innerText="位于监测点 "+String(minAngle)+"-"+String(maxAngle)+"° 的方向上";
		console.log(minAngle,maxAngle);
                if(angle=="左侧") c=45;
                else if(angle=="前方") c=90;
                else if(angle=="右侧") c=135;
                Charts[deviceId].setOption({
                	series: [{
                                startAngle: 180,
            			data: [[d,minAngle],[d,maxAngle]]
                                //[[d-0.1,c-3],[d+0.1,c+3],[d,c],[d+0.1,c-3],[d-0.1,c+3]]
        		}],
                });
            }
            else if (distance == '0.00m') {
                document.getElementById("distance").innerText="目标区域空旷，无\"距离\"参数";
                document.getElementById("angle").innerText="目标区域空旷，无\"方向\"参数"; 
                Charts[deviceId].setOption({
                	series: [{
            			data: [[0,0],[0,0]]
        		}],
                });
            }
            
        } else  if (LastOutcome == -1){
            document.getElementById("distance").innerText='';
            document.getElementById("angle").innerText='';
            showInfo("未检测到信号！设备未在线");
            Charts[deviceId].setOption({
                series: [{
            		data: [[0,0],[0,0]],
        	}],
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
