const { Document, Packer, Paragraph, TextRun, HeadingLevel, Alignment } = require('docx');

// 创建文档
const doc = new Document({
    sections: [{
        properties: {},
        children: [
            // 标题
            new Paragraph({
                text: "产品经理可视化工作流",
                heading: HeadingLevel.HEADING_1,
                alignment: Alignment.CENTER,
                spacing: {
                    after: 500,
                },
            }),
            new Paragraph({
                text: "Gemini + Banana Pro 实战",
                heading: HeadingLevel.HEADING_2,
                alignment: Alignment.CENTER,
                spacing: {
                    after: 500,
                },
            }),
            
            // 作者信息
            new Paragraph({
                text: "陈卓|frankechen",
                alignment: Alignment.CENTER,
                spacing: {
                    after: 400,
                },
            }),
            
            // 一、适用场景
            new Paragraph({
                text: "一、适用场景",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 400,
                    after: 200,
                },
            }),
            
            // 二、从想法到出图的具体落地
            new Paragraph({
                text: "二、从想法到出图的具体落地",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 400,
                    after: 200,
                },
            }),
            
            // 三、关键方法：如何稳定产出高质量的图？
            new Paragraph({
                text: "三、关键方法：如何稳定产出高质量的图？",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 400,
                    after: 200,
                },
            }),
            
            // 案例部分
            new Paragraph({
                text: "案例",
                heading: HeadingLevel.HEADING_3,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            
            // 设计风格Prompt部分
            new Paragraph({
                text: "设计风格Prompt",
                heading: HeadingLevel.HEADING_3,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "简笔画风格",
                heading: HeadingLevel.HEADING_4,
                spacing: {
                    before: 100,
                    after: 50,
                },
            }),
            
            new Paragraph({
                text: "学术海报风",
                heading: HeadingLevel.HEADING_4,
                spacing: {
                    before: 100,
                    after: 50,
                },
            }),
            
            new Paragraph({
                text: "粘土拟物风",
                heading: HeadingLevel.HEADING_4,
                spacing: {
                    before: 100,
                    after: 50,
                },
            }),
            
            new Paragraph({
                text: "扁平化矢量插画风格",
                heading: HeadingLevel.HEADING_4,
                spacing: {
                    before: 100,
                    after: 200,
                },
            }),
            
            // 附录部分
            new Paragraph({
                text: "附录",
                heading: HeadingLevel.HEADING_2,
                spacing: {
                    before: 400,
                    after: 200,
                },
            }),
            
            new Paragraph({
                text: "Banana详解",
                heading: HeadingLevel.HEADING_3,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            
            new Paragraph({
                text: "设计风格Prompt",
                heading: HeadingLevel.HEADING_3,
                spacing: {
                    before: 200,
                    after: 100,
                },
            }),
            
            // 日期信息
            new Paragraph({
                text: "01/15 更新",
                alignment: Alignment.RIGHT,
                spacing: {
                    after: 400,
                },
            }),
        ]
    }]
});

// 生成文档
Packer.toBuffer(doc).then(buffer => {
    require('fs').writeFileSync('产品经理可视化工作流.docx', buffer);
    console.log('文档生成成功：产品经理可视化工作流.docx');
}).catch(err => {
    console.error('生成文档时出错：', err);
});