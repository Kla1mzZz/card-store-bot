import aiofiles

async def format_file_lines(file_path: str):
    result = []
    
    async with aiofiles.open(file_path, mode='r') as file:
        async for line in file:
            line = line.strip()
            parts = [part.strip() for part in line.split('|')]
            formatted_line = '|'.join(parts)
            result.append(formatted_line)
    return result
