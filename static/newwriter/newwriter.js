$(function() {
    var checkAll = false;

    $('.check-all').on('click', function() {
        checkAll = !checkAll;
        $('.id-checks').prop("checked", checkAll);
    });

	$('#closeAllotDialog').on('click', function() {
		$('.allot-task-view').hide();
	});

    $('.task-allot').on('click', function() {
		var ipList = [];
        $allotView = $('.allot-task-view');
		$('.id-checks:checked').each(function() {
			ipList.push(this.value);
		});
		console.log(ipList);

		if (ipList.length < 1) {
			alert("至少选择一部作品！");
			return;
		}
        $.ajax({
            type: "GET",
            url: '/user/api/list',
            data: {
                crm: '4_1_6',
                pn: '1',
                rn: '100'
            },
            dataType: "json",
            success: function(data){
                if (data.error) {
                    alert('数据请求失败，请重新刷新页面！');
                    return;
                }
                console.log(data);
                $allotView.show();

                var index, item, html = '';
                for (index in data.list) {
                    item = data.list[index];
                    html += '<p style="margin: 0;height: 24px;">'
                                + '<input type="checkbox" class="i-checks" name="verify_user" value="'+item.uid+'"> &nbsp; <label>'+item.name+'</label>'
                            + '</p>';
                }

                $allotView.find('.user-list').html(html);

            },
            error: function() {
                alert('数据请求失败，请重新刷新页面！');
            }
        });
    });

    $('.checkVerifyResult').on('click', function() {
        var newWriterId = $(this).data("newwriterid");
        var verifyStatus = $(this).data("status");
        var $verifyResultView = $('#verifyResultView')

        $.ajax({
            type: "GET",
            url: '/newwriter/api/verifyResult',
            data: {
                newWriterId: newWriterId
            },
            dataType: "json",
            success: function(data){
                if (data.error) {
                    alert('数据请求失败，请重新刷新页面！');
                    return;
                }

                console.log(data);
                $('.checkResult').show();

                var index, item, score = 0, html = '';
                for (index in data.list) {
                    item = data.list[index];
                    score += (item.story + item.structure + item.character + item.market);

                    if (item.status != -1){
                        html += '<p><b>' + item.rms.name + '&nbsp;&nbsp;</b>'
                                + '故事:&nbsp;&nbsp;<span class="text-navy">' + item.story + '分</span>&nbsp;&nbsp;' 
								+ '结构:&nbsp;&nbsp;<span class="text-navy">' + item.structure + '分</span>&nbsp;&nbsp;'
                                + '人物:&nbsp;&nbsp;<span class="text-navy">' + item.character + '分</span>&nbsp;&nbsp;'
                                + '市场:&nbsp;&nbsp;<span class="text-navy">' + item.market + '分</span>&nbsp;&nbsp;'
                            + '</p>';
                    } else {
                        html += '<p><b>' + item.rms.name + '&nbsp;&nbsp;</b>'
                                + '<span class="text-warning">未评审</span>'
                            + '</p>';
                    }
                }

                $verifyResultView.find('.verify-result').html(html);

                if (verifyStatus == 1) {
                    $verifyResultView.find('.show-score').show().find('.score').text(score / data.list.length);
                }
            },
            error: function() {
                alert('数据请求失败，请重新刷新页面！');
            }
        });
    });

    $('#task-allot-btn').on('click', function() {
        var ipList = [],
            adminList = [],
            everyoneNum = $('#everyone-num').val();
		$('.id-checks:checked').each(function() {
			ipList.push(this.value);
		});

		$('input[name="verify_user"]:checked').each(function() {
		    adminList.push(this.value);
		});

		if (ipList.length < 1) {
			alert("至少选择一部作品！");
			return;
		}

		if (adminList.length < 1) {
			alert("至少选择一个评审人员！");
			return;
		}

		if (!everyoneNum || everyoneNum < 1) {
            alert('请填写正确的评审次数！');
            return;
        }

        if (everyoneNum > adminList.length) {
            alert('每部IP被评审的次数,不能大于评审人员的总数!');
            return;
        }

        $.ajax({
            type: "GET",
            url: '/newwriter/api/allot',
            data: {
                ipList: ipList.join(','),
                adminList: adminList.join(','),
				everyoneNum: everyoneNum
            },
            dataType: "json",
            success: function(data){
                if (data.error) {
                    alert('数据请求失败，请重新刷新页面！');
                    return;
                }
                alert('分配成功！');
                window.location.reload();
            },
            error: function() {
                alert('数据请求失败，请重新刷新页面！');
            }
        });
    });

    $('.export-excel-btn').on('click', function() {
        $('.export-layer').show();
    });

    $('.close-export-layer').on('click', function() {
        $('.export-layer').hide();
    });

    $('.export-csv').on('click', function() {
        var startId = $('input[name="startId"]').val();
        var endId = $('input[name="endId"]').val();
        var token = $('input[name="token"]').val();

        if (!endId || !startId) {
            alert('请好好填写需要导出的起始和截止编号!');
            return false;
        }
        if (endId < startId) {
            alert('请不要胡乱填写,截止编号是不能小于起始编号的!');
            return false;
        }

        if(!window.confirm('你确定要导出报表吗？')){
            return false;
        }

        window.open('http://y.yunlaiwu.com/filter/exportnewwritercsv?t=api&startId=' + startId + "&endId=" + endId + "&token=" + token);
    });
});

