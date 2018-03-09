    var $layer = $('.checkResult');
    window.newWriterId = null;

    function score(newWriterId) {
        $layer.show();
        window.newWriterId = newWriterId;
    }

    function updateScore(newWriterId, story, structure, character, market) {
        window.newWriterId = newWriterId;
        $layer.find('input[name="story"]').val(story);
        $layer.find('input[name="structure"]').val(structure);
        $layer.find('input[name="character"]').val(character);
        $layer.find('input[name="market"]').val(market);
        $layer.show();
    }

    function submitScore() {
        var story = $layer.find('input[name="story"]').val();
        var structure =$layer.find('input[name="structure"]').val();
        var character =$layer.find('input[name="character"]').val();
        var market =$layer.find('input[name="market"]').val();

        if (!window.newWriterId) {
            alert("无效ID！");
            return;
        }

        if(!story || story > 20 || story < 0) {
            alert("请输出正确的分数,故事满分20");
            return;
        }

        if(!structure || structure > 40 || structure < 0) {
            alert("请输出正确的分数,结构满分40");
            return;
        }

        if(!character || character > 30 || character < 0) {
            alert("请输出正确的分数,人物满分30");
            return;
        }

        if(!market || market > 10 || market < 0) {
            alert("请输出正确的分数,市场满分10");
            return;
        }

        $.ajax({
            url: '/newwriter/api/verify',
            type: "GET",
            data: {
                newWriterId: newWriterId,
                story: story,
                structure: structure,
                character: character,
                market: market,
            },
            dataType: "json",
            success: function(res){
                if (res.error) {
                    alert('数据请求失败，请重新刷新页面！');
                    return;
                }
                alert('打分成功!');
                window.location.reload();
            },
            error: function() {
                alert('数据请求失败，请重新刷新页面！');
            }
        });
    }

