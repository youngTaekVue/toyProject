/**
 * 컴포넌트 1
 * 
 * @param array : 생성할 객체 리스트
 * @return 컴포넌트 생성후 div text 리턴
 */
export function COMP1(array) {
    let divContent = "";
    console.log(array);


    for (var j = 0; j < array.length; j++) {

        let color = array[j].hex;

        divContent += "<div class='item' style='background-color: " + color + ";'><div class='copy'>" + color + "</div></div>";

    }
    return divContent;
}