import * as CUSTOM from './helper.js';
import chunkArray from './sliceContent.js';

/**
 * onLoadJson
 */
function onloadJson() {
    var content = "";
    //access your JSON file through the variable "json"
    $.getJSON("data/color.json", function(json) {


        let bRankData = Array.from(json);

        // chunkArray(data,itemsPerRender) to get array of small arrays
        const chunckedArray = chunkArray(bRankData, 100);
        console.log(chunckedArray);
        content = CUSTOM.COMP1(chunckedArray[pageNum]);
        console.log(content);
        $("#list").append(content);
    });
}


let pageNum = 0;
let loding = false;
let addItemList = [];

$(function() {
    onloadJson();
});