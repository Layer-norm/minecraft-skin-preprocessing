# written by https://lingma.aliyun.com/

import unittest
import os
import tempfile
import shutil
from PIL import Image
import base64
from io import BytesIO

try:
    from src.mcskinprep.tools import MCSkinTools, MCSkinFileProcessor
except ImportError:
    # 如果上面的方式失败，则尝试相对导入
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from mcskinprep.tools import MCSkinTools, MCSkinFileProcessor


class TestMCSkinTools(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.skin_tools = MCSkinTools()
        
        # 创建一个简单的64x32测试图像
        self.test_img_64x32 = Image.new('RGBA', (64, 32), (255, 0, 0, 255))
        # 添加一些可识别的像素以便验证转换
        for x in range(8, 24):
            for y in range(0, 8):
                self.test_img_64x32.putpixel((x, y), (0, 255, 0, 255))  # 绿色方块
        
        # 创建一个64x64测试图像
        self.test_img_64x64 = Image.new('RGBA', (64, 64), (0, 0, 255, 255))
        for x in range(40, 56):
            for y in range(0, 8):
                self.test_img_64x64.putpixel((x, y), (255, 255, 0, 255))  # 黄色方块
    
    def test_convert_skin_64x32_to_64x64(self):
        """Test conversion from 64x32 to 64x64."""
        result = self.skin_tools.convert_skin_64x32_to_64x64(self.test_img_64x32)
        
        # 验证输出尺寸
        self.assertEqual(result.size, (64, 64))
        
        # 验证某些像素是否正确转换
        self.assertEqual(result.getpixel((8, 0)), (0, 255, 0, 255))  # 原始绿色方块应保留
        self.assertEqual(result.getpixel((0, 32)), (0, 0, 0, 0))     # 新区域应透明
    
    def test_swap_skin_layer2_to_layer1(self):
        """Test swapping layers."""
        result = self.skin_tools.swap_skin_layer2_to_layer1(self.test_img_64x64)
        
        # 验证输出尺寸
        self.assertEqual(result.size, (64, 64))
    
    def test_remove_layer(self):
        """Test removing layers."""
        # 测试移除第一层
        result_layer1 = self.skin_tools.remove_layer(self.test_img_64x64, 1)
        self.assertEqual(result_layer1.size, (64, 64))
        
        # 测试移除第二层
        result_layer2 = self.skin_tools.remove_layer(self.test_img_64x64, 2)
        self.assertEqual(result_layer2.size, (64, 64))
        
        # 测试无效图层索引
        result_invalid = self.skin_tools.remove_layer(self.test_img_64x64, 3)
        self.assertIsNone(result_invalid)
    
    def test_load_skin_from_base64(self):
        """Test loading skin from base64 string."""
        # 将测试图像转换为base64
        buffer = BytesIO()
        self.test_img_64x32.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        # 加载并验证
        loaded_img = MCSkinTools.load_skin_from_base64(img_str)
        self.assertEqual(loaded_img.size, (64, 32))


class TestMCSkinFileProcessor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.processor = MCSkinFileProcessor()
        
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.temp_dir, "input")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 创建测试图像文件
        self.test_img_64x32 = Image.new('RGBA', (64, 32), (255, 0, 0, 255))
        self.test_img_64x64 = Image.new('RGBA', (64, 64), (0, 0, 255, 255))
        
        self.test_file_64x32 = os.path.join(self.input_dir, "test_skin_64x32.png")
        self.test_file_64x64 = os.path.join(self.input_dir, "test_skin_64x64.png")
        
        self.test_img_64x32.save(self.test_file_64x32)
        self.test_img_64x64.save(self.test_file_64x64)
    
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)
    
    def test_convert_skin_64x32_to_64x64_file(self):
        """Test file-based conversion from 64x32 to 64x64."""
        output_file = os.path.join(self.output_dir, "converted_skin.png")
        
        # 执行转换
        success = self.processor.convert_skin_64x32_to_64x64(self.test_file_64x32, output_file)
        
        # 验证结果
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))
        
        # 验证输出图像
        with Image.open(output_file) as result_img:
            self.assertEqual(result_img.size, (64, 64))
    
    def test_swap_skin_layer2_to_layer1_file(self):
        """Test file-based layer swapping."""
        output_file = os.path.join(self.output_dir, "swapped_skin.png")
        
        # 执行交换
        success = self.processor.swap_skin_layer2_to_layer1(self.test_file_64x64, output_file)
        
        # 验证结果
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))
        
        # 验证输出图像
        with Image.open(output_file) as result_img:
            self.assertEqual(result_img.size, (64, 64))
    
    def test_twice_swap_skin_layers_file(self):
        """Test double layer swapping."""
        output_file = os.path.join(self.output_dir, "double_swapped_skin.png")
        
        # 执行双交换
        success = self.processor.twice_swap_skin_layers(self.test_file_64x64, output_file)
        
        # 验证结果
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))
        
        # 验证输出图像
        with Image.open(output_file) as result_img:
            self.assertEqual(result_img.size, (64, 64))
    
    def test_remove_layer_file(self):
        """Test file-based layer removal."""
        output_file = os.path.join(self.output_dir, "removed_layer_skin.png")
        
        # 移除第一层
        success = self.processor.remove_layer(self.test_file_64x64, output_file, layer_index=1)
        
        # 验证结果
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))
        
        # 验证输出图像
        with Image.open(output_file) as result_img:
            self.assertEqual(result_img.size, (64, 64))
    
    def test_batch_convert_folder(self):
        """Test batch conversion of folder."""
        # 执行批量转换
        self.processor.batch_convert_folder(
            convert_func=self.processor.convert_skin_64x32_to_64x64,
            input_folder=self.input_dir,
            output_folder=self.output_dir,
            overwrite=True
        )


if __name__ == '__main__':
    unittest.main()