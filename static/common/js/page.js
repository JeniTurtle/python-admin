$(document).ready(function(){

    //最多显示页数
    var max_page = 9;

	//每页显示的数目

	var show_per_page = parseInt($('#page_num').val());

	//获取content对象里面，数据的数量

	var number_of_items = parseInt($('#total_num').val());

	//计算页面显示的数量

	var number_of_pages = Math.ceil(number_of_items/show_per_page);

	//隐藏域默认值

	var current_page = parseInt($('#current_page').val());

	$('#page_num').val(show_per_page);



	var navigation_html = '<a class="previous_link'+ (current_page <=1 ? ' invalid_page' : '') +'" href="javascript:'+(current_page > 1 ? 'previous()' : 'void(0)')+';">上一页</a>';

	var current_link = 1;

	if (max_page > number_of_pages) {
        finally_link = number_of_pages;
	} else {
	    if (current_page < max_page) {
	        finally_link = max_page;
	        current_link = 1
	    } else if (current_page > number_of_pages - parseInt(max_page / 2)) {
	        finally_link = number_of_pages;
	        current_link = number_of_pages - max_page + 1;
	    } else {
	        current_link = current_page - parseInt(max_page / 2);
	        finally_link = current_page + parseInt(max_page / 2);
	    }
	}

	while(finally_link >= current_link){

		navigation_html += '<a class="page_link" href="javascript:go_to_page(' + current_link +', ' + show_per_page +')" longdesc="' + current_link +'">'+  current_link +'</a>';

		current_link++;

	}

	navigation_html += '<a class="next_link'+ (number_of_pages <= current_page ? ' invalid_page' : '') +'" href="javascript:'+(number_of_pages > current_page ? 'next()' : 'void(0)')+';">下一页</a>';



	$('#page_navigation').html(navigation_html);



	//add active_page class to the first page link

	$('#page_navigation .page_link[longdesc='+current_page+']').attr('id', 'active_page');



	//隐藏该对象下面的所有子元素

	$('#content').children().css('display', 'none');



	//显示第n（show_per_page）元素

	$('#content').children().slice(0, show_per_page).css('display', 'block');

	$('#jump-page').keydown(function(event) {
        if (event.keyCode != 13) {
            return;
        }
        var val = parseInt($(this).val());
        if (val > number_of_pages) {
            val = number_of_pages;
        }
        go_to_page(val, show_per_page);
    });

});



//上一页

function previous(){

	var new_page = parseInt($('#current_page').val()) - 1;
    var show_per_page = parseInt($('#page_num').val());
    go_to_page(new_page, show_per_page);


}

//下一页

function next(){
	var new_page = parseInt($('#current_page').val()) + 1;
	var show_per_page = parseInt($('#page_num').val());

	go_to_page(new_page, show_per_page);
}

//跳转某一页

function go_to_page(current_page, show_per_page){
    url = addUrlParam(window.location.href, 'pn', current_page);
    window.location.href = addUrlParam(url, 'rn', show_per_page);
}

function addUrlParam(url, name, value) {
    var currentUrl = url.split('#')[0];
    if (/\?/g.test(currentUrl)) {
        re = eval('/('+ name+'=)([^&]*)/gi');
        if (re.test(currentUrl)) {
            currentUrl = currentUrl.replace(re, name + "=" + value);
        } else {
            currentUrl += "&" + name + "=" + value;
        }
    } else {
        currentUrl += "?" + name + "=" + value;
    }
    if (url.split('#')[1]) {
        return currentUrl + '#' + url.split('#')[1];
    } else {
        return currentUrl;
    }
}