
class MarkdownToJsonConverter:
    def __init__(self, markdown_text):
        self.text = markdown_text
        self.json_data = {
            "title": None,
            "headers": [],
            "paragraphs": [],
            "lists": [],
            "links": [],
            "images": [],
            "tables": [],
            "code_blocks": [],
            "blockquotes": []
        }

    def parse_headers(self):
        headers = re.findall(r"^(#{1,6})\s+(.*)", self.text, re.MULTILINE)
        for header in headers:
            self.json_data["headers"].append({
                "level": len(header[0]),
                "text": header[1]
            })
        if headers and len(headers[0][0]) == 1:
            self.json_data["title"] = headers[0][1]

    def parse_paragraphs(self):
        paragraphs = re.split(r"\n\n+", self.text)
        for para in paragraphs:
            if not para.startswith("#") and not para.startswith("-") and not re.search(r"\[(.*?)\]\((.*?)\)", para):
                self.json_data["paragraphs"].append(para.strip())

    def parse_lists(self):
        lists = re.findall(r"(?m)^[-*+]\s+(.*)", self.text)
        if lists:
            self.json_data["lists"].append(lists)

    def parse_links(self):
        links = re.findall(r"\[(.*?)\]\((.*?)\)", self.text)
        for link in links:
            self.json_data["links"].append({
                "text": link[0],
                "url": link[1]
            })

    def parse_images(self):
        images = re.findall(r"!\[(.*?)\]\((.*?)\)", self.text)
        for image in images:
            self.json_data["images"].append({
                "alt_text": image[0],
                "url": image[1]
            })

    def parse_tables(self):
        tables = re.findall(r"(?:\|.+?\|\n)+", self.text)
        for table in tables:
            rows = [row.strip().split("|")[1:-1] for row in table.split("\n") if row.startswith("|")]
            if rows:
                headers = rows[0]
                data_rows = rows[1:]
                self.json_data["tables"].append({
                    "headers": headers,
                    "rows": data_rows
                })

    def parse_code_blocks(self):
        code_blocks = re.findall(r"```(.*?)\n(.*?)```", self.text, re.S)
        for block in code_blocks:
            self.json_data["code_blocks"].append({
                "language": block[0].strip(),
                "code": block[1].strip()
            })

    def parse_blockquotes(self):
        blockquotes = re.findall(r"^>\s+(.*)", self.text, re.MULTILINE)
        for quote in blockquotes:
            self.json_data["blockquotes"].append(quote.strip())

    def convert(self):
        self.parse_headers()
        self.parse_paragraphs()
        self.parse_lists()
        self.parse_links()
        self.parse_images()
        self.parse_tables()
        self.parse_code_blocks()
        self.parse_blockquotes()
        return json.dumps(self.json_data, indent=4)

# Example usage: