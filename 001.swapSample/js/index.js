import * as CUSTOM from './helper.js';

/**
 * onLoadJson
 */
function onloadJson() {
    var content = "";
    //access your JSON file through the variable "json"
    $.getJSON("data/testData.json", function(json) {
        bRankData = json;
        content = CUSTOM.COMP1(bRankData);
        $("#content").append(content);

        // 3초마다 특정 객체에 대해 점수 set & 순서 재 조정
        setInterval(function() {
            CUSTOM.changeRandomScore(bRankData, refreshTime).then(function() {
                bRankData.forEach(function(contents, i) {
                    let len = $("#content_" + bRankData[i].userId);
                    prevPosition[contents.userId] = len[0].getBoundingClientRect().top;
                });

                CUSTOM.bubbleSort(bRankData).then(function(sortedData) {
                    let reContent = CUSTOM.COMP1(sortedData);
                    $("#content").children().remove();
                    $("#content").append(reContent);

                    CUSTOM.changeNum(CUSTOM.arrChScore);

                    // swap position after sorted
                    sortedData.forEach(function(contents) {
                        let len2 = $("#content_" + contents.userId);
                        let newTop = len2[0].getBoundingClientRect().top;
                        let prevTop = prevPosition[contents.userId];

                        let diffY = prevTop - newTop;
                        if (diffY) {
                            // swap position after sorted
                            CUSTOM.swapElement(len2[0], diffY, refreshTime);
                        }
                    });
                });


            })
        }, 3000);
    });
}

let bRankData = [];
let prevPosition = [];
const refreshTime = 200;

$(function() {
    onloadJson();
});