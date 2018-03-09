
function checkResult(objectId, firstStatus, secondStatus, thirdStatus, isOldData) {
    $.ajax({
        type: "GET",
        url: "/ippool/api/verifyResult",
        data: {
            objectId: objectId
        },
        dataType: "json",
        success: function(data){
            if (data.error) {
                alert('数据请求失败，请重新刷新页面！');
                return;
            }
            console.log(data);
            $checkResult = $('.checkResult');
            $checkResult.show();

            $firstResult = $checkResult.find('.first-result');

            if (data.first && data.first.length > 0) {

                $firstResult.find('.verify-list').html('');

                var passCount = 0, notPassCount = 0, isVerified = true;

                for (var index in data.first) {
                    var item = data.first[index];
                    var $p = $('<p>'+item.username+'</p>')
                    var $span = $('<span style="padding-left: 12px"></span>')
                    if (item.verifyResult == 0) {
                        $span.text('待评审');
                        $span.addClass('text-warning');
                        isVerified = false;
                    } else if (item.verifyResult == 1) {
                        $span.text('通过');
                        $span.addClass('text-navy');
                        passCount += 1
                    } else if (item.verifyResult == 2) {
                        $span.text('不通过');
                        $span.addClass('text-danger');
                        notPassCount += 1
                    }
                    $p.append($span).append('<span style="padding-left: 12px">'+item.updateAt+'</span>');
                    $firstResult.find('.verify-list').append($p);
                }

                var verify_html = '';

                if (isOldData == 1) {
                    verify_html += '<span class="text-danger">（历史灌入数据）</span>';
                } else {
                    if (firstStatus == 0)
                        verify_html = '<span class="text-warning">（待审核）</span>'
                    else if (firstStatus == 1)
                        verify_html = '<span class="text-navy">（通过）</span>'
                    else
                        verify_html = '<span class="text-danger">（不通过）</span>'

                    if (isVerified && (passCount > notPassCount ? 1 : 2) != firstStatus && item.ipAllotId != -1) {
                        $firstResult.find('.result-is-modify').show();
                    } else {
                        $firstResult.find('.result-is-modify').hide();
                    }
                }

                $firstResult.find('.result-is-modify').siblings().remove();
                $firstResult.find('.result-is-modify').before(verify_html);
                $firstResult.show();
            } else {
                $firstResult.hide();
            }

            $secondResult = $checkResult.find('.second-result');

            if (data.second && data.second.length > 0) {

                $secondResult.find('.verify-list').html('');

                var passCount = 0, notPassCount = 0, isVerified = true;

                for (var index in data.second) {
                    var item = data.second[index];
                    var $p = $('<p>'+item.username+'</p>')
                    var $span = $('<span style="padding-left: 12px"></span>')
                    if (item.verifyResult == 0) {
                        $span.text('待评审');
                        $span.addClass('text-warning');
                        isVerified = false;
                    } else if (item.verifyResult == 1) {
                        $span.text('精品');
                        $span.addClass('text-navy');
                        passCount += 1
                    } else if (item.verifyResult == 2) {
                        $span.text('非精品');
                        $span.addClass('text-danger');
                        notPassCount += 1
                    }
                    $p.append($span).append('<span style="padding-left: 12px">'+item.updateAt+'</span>');
                    $secondResult.find('.verify-list').append($p);
                }

                var verify_html = '';

                if (isOldData == 1) {

                    verify_html += '<span class="text-danger">（历史灌入数据）</span>';

                } else {
                    if (secondStatus == 0)
                        verify_html = '<span class="text-warning">（待审核）</span>'
                    else if (secondStatus == 1)
                        verify_html = '<span class="text-navy">（通过）</span>'
                    else
                        verify_html = '<span class="text-danger">（不通过）</span>'

                    if (isVerified && (passCount > notPassCount ? 1 : 2) != secondStatus) {
                        $secondResult.find('.result-is-modify').show();
                    } else {
                        $secondResult.find('.result-is-modify').hide();
                    }
                }

                $secondResult.find('.result-is-modify').siblings().remove();
                $secondResult.find('.result-is-modify').before(verify_html);
                $secondResult.show();
            } else {
                $secondResult.hide()
            }

            $thirdResult = $checkResult.find('.third-result');
            if (data.third && data.third.length > 0) {

                $thirdResult.find('.verify-list').html('');

                var passCount = 0, notPassCount = 0, isVerified = true;

                for (var index in data.third) {
                    var item = data.third[index];
                    var $p = $('<p>'+item.username+'</p>')
                    var $span = $('<span style="padding-left: 12px"></span>')
                    if (item.verifyResult == 0) {
                        $span.text('待评审');
                        $span.addClass('text-warning');
                        isVerified = false;
                    } else if (item.verifyResult == 1) {
                        $span.text('精品');
                        $span.addClass('text-navy');
                        passCount += 1;
                    } else if (item.verifyResult == 2) {
                        $span.text('非精品');
                        $span.addClass('text-danger');
                        notPassCount += 1
                    }
                    $p.append($span).append('<span style="padding-left: 12px">'+item.updateAt+'</span>');
                    $thirdResult.find('.verify-list').append($p);
                }

                var verify_html = '';

                if (isOldData == 1) {

                    verify_html += '<span class="text-danger">（历史灌入数据）</span>';

                } else {
                    if (thirdStatus == 0)
                        verify_html = '<span class="text-warning">（待审核）</span>'
                    else if (thirdStatus == 1)
                        verify_html = '<span class="text-navy">（通过）</span>'
                    else
                        verify_html = '<span class="text-danger">（不通过）</span>'

                    if (isVerified && (passCount > notPassCount ? 1 : 2) != thirdStatus) {
                        $thirdResult.find('.result-is-modify').show();
                    } else {
                        $firstResult.find('.result-is-modify').hide();
                    }
                }

                $thirdResult.find('.result-is-modify').siblings().remove();
                $thirdResult.find('.result-is-modify').before(verify_html);
                $thirdResult.show();
            } else {
                $thirdResult.hide()
            }

            var marginTop = ($(window).height() - $('.modal-dialog').height()) / 2;
            $('.modal-dialog').css({
                'margin-top': marginTop
            });
        },
        error: function() {
            alert('数据请求失败，请重新刷新页面！');
        }
    });
}
