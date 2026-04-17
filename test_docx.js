const { Document, Packer, Paragraph, TextRun } = require('docx');
const fs = require('fs');

const doc = new Document({
    sections: [{
        children: [
            new Paragraph({
                children: [new TextRun({ text: "Hello World", bold: true })]
            })
        ]
    }]
});

Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync("test.docx", buffer);
    console.log("Done!");
}).catch(err => {
    console.error("Error:", err);
});
