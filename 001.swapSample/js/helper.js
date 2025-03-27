export let arrChScore = []; // array : [0] id, [1] score, [2] increased score

/**
 * 컴포넌트 1
 * 
 * @param array : 생성할 객체 리스트
 * @return 컴포넌트 생성후 div text 리턴
 */
export function COMP1(array) {
    let divContent = "";
    for (var i = 0; i < array.length; i++) {
        let strNo = i + 1;
        let strId = array[i].userId;
        let strName = array[i].displayName;
        let strPicture = array[i].picture;
        let strScore = array[i].score;
   
        divContent += "<div class='content' id='content_" + strId + "'>" +
            "<div class='ranking-no'>" + strNo + "</div>" +
                "<div class='picture increIcon'>" +
                    "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-arrow-up-short' viewBox='0 0 16 16'>"+
                        "<path fill-rule='evenodd' d='M8 12a.5.5 0 0 0 .5-.5V5.707l2.146 2.147a.5.5 0 0 0 .708-.708l-3-3a.5.5 0 0 0-.708 0l-3 3a.5.5 0 1 0 .708.708L7.5 5.707V11.5a.5.5 0 0 0 .5.5'/>"+
                    "</svg>"+ 
                "<span id='increNum_" + strId +"'></span>"+
                "</div>" +
            "<div class='display-name id='name_" + strId + "'>" + strName + " </div>" +
            "<div class='score' id='score_" + strId + "'>" + strScore + "</div>" +
            "</div>"
    }
    return divContent;
}

/**
 * Change Scores of every content (Random)
 * 
 * @param Array  arr
 * @param Number refreshTime
 */
export async function changeRandomScore(bRankData, refreshTime) {
    return await new Promise(function(resolve) {

        var targetNo = Math.floor(Math.random() * bRankData.length);
        var randomNum = Math.floor(Math.random() * 100);
        let frame = 0;
        let timer = setInterval(function() {
            frame++;
            let progress = frame / 60;

            bRankData[targetNo].icScore = bRankData[targetNo].score + Math.floor(randomNum);
            if (progress == 1) {

                clearInterval(timer);
          
                // id, score, increased score
                arrChScore = [bRankData[targetNo].userId, bRankData[targetNo].score, bRankData[targetNo].icScore,Math.floor(randomNum)];
                bRankData[targetNo].score = bRankData[targetNo].icScore;
                resolve(bRankData);
            }
        }, refreshTime / 60);
    });
}

/**
 * increased Scores
 * @param Array  array : [0] id, [1] score, [2] increased score
 */
export function changeNum(array) {
    let target = $("#score_" + array[0]);
    let beforeScore = array[1];
    let afterScore = array[2];
    let incresScore = array[3];
    

    $(".increIcon").append("");
    $("#increNum_" + array[0]).text(incresScore);

    let increased = setInterval(function() {
        beforeScore++;
        if (beforeScore > afterScore) {
            clearInterval(increased);
        } else {
            target.text(beforeScore);
        }
    }, 12.738853);
}

/**
 * Bubble Sroting
 * @param Array arr
 */
export async function bubbleSort(arr) {
    return await new Promise(function(resolve) {
        let tmp = 0;
        for (let i = arr.length - 1; i >= 0; i--) {
            for (let j = i - 1; j >= 0; j--) {
                if (arr[i].score > arr[j].score) {
                    tmp = arr[j];
                    arr[j] = arr[i];
                    arr[i] = tmp;
                }
            }
        }
        resolve(arr);
    });
}

/**
 * Swap animation
 *
 * @param Object target
 * @param Number swapHeight
 * @param Number duration
 */
export function swapElement(target, swapHeight, duration) {
    // if ranking has any changed, swap element.
    requestAnimationFrame(function() {
        // swap the contentEl to old position
        target.style.transform = "translateY(" + swapHeight + "px)";
        target.style.transition = "transform 0s";

        requestAnimationFrame(function() {
            // swap the contentEl back to now postion
            target.style.transform = "";
            target.style.transition = "transform " + duration + "ms";
        });
    });
}