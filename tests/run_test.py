# written by https://lingma.aliyun.com/

import unittest
import os
import tempfile
import shutil
from PIL import Image
import base64
from io import BytesIO

from mcskinprep import MCSkinTools, MCSkinFileProcessor, MCSkinType, MCSkinRegionDetector


class TestMCSkinTools(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.skin_tools = MCSkinTools()
        self.skin_type_detector = MCSkinType()
        self.region_detector = MCSkinRegionDetector()
        
        # 创建一个简单的64x32测试图像
        self.test_img_64x32 = Image.new('RGBA', (64, 32), (255, 0, 0, 255))  # 红色方块
        # 添加一些可识别的像素以便验证转换
        # head1_layer1
        for x in range(8, 24):
            for y in range(0, 8):
                self.test_img_64x32.putpixel((x, y), (0, 255, 0, 255))  # 绿色方块

        
        # right_arm2_layer1
        for x in range(40, 56):
            for y in range(20, 32):
                self.test_img_64x32.putpixel((x, y), (255, 255, 0, 255))  # 黄色方块
        
        # 创建一个64x64测试图像
        self.test_img_64x64 = Image.new('RGBA', (64, 64), (255, 0, 0, 255))  # 红色方块

        # head1_layer1
        for x in range(8, 24):
            for y in range(0, 8):
                self.test_img_64x64.putpixel((x, y), (0, 255, 0, 255))  # 绿色方块

        
        # right_arm2_layer1
        for x in range(40, 56):
            for y in range(20, 32):
                self.test_img_64x64.putpixel((x, y), (255, 255, 0, 255))  # 黄色方块

        # left_arm2_layer1
        for x in range(32, 48):
            for y in range(52, 64):
                self.test_img_64x64.putpixel((x, y), (255, 255, 0, 255))  # 黄色方块

    def test_skin_regions_for_regular_type(self):
        """Test skin regions for regular skin type."""
        skin_type_handler = MCSkinType('regular')
        regions = skin_type_handler.skin_regions
        
        # 检查regular类型的手臂区域宽度是否正确(4像素宽)
        right_arm_coords = regions['layer1']['right_arm'][0]['coords']
        arm_width = right_arm_coords[2] - right_arm_coords[0]
        self.assertEqual(arm_width, 8)  # 右臂部分应该是8像素宽

        # 检查特定区域坐标是否符合预期
        head_layer1_coords = regions['layer1']['head'][0]['coords']
        self.assertEqual(head_layer1_coords, [8, 0, 24, 8])
        
        head_layer2_coords = regions['layer2']['head'][0]['coords']
        self.assertEqual(head_layer2_coords, [40, 0, 56, 8])

    def test_skin_regions_for_slim_type(self):
        """Test skin regions for slim type."""
        skin_type_handler = MCSkinType('slim')
        regions = skin_type_handler.skin_regions
        
        # 检查slim类型的手臂区域宽度是否正确(3像素宽)
        right_arm_coords = regions['layer1']['right_arm'][0]['coords']
        arm_width = right_arm_coords[2] - right_arm_coords[0]
        self.assertEqual(arm_width, 6)  # slim手臂应该比regular窄2像素
        
        # 检查其他区域不受影响
        head_layer1_coords = regions['layer1']['head'][0]['coords']
        self.assertEqual(head_layer1_coords, [8, 0, 24, 8])  # 头部坐标应该不变

    def test_invalid_skin_type_raises_error(self):
        """Test that invalid skin type raises ValueError."""
        skin_type_handler = MCSkinType('invalid_type')
        
        with self.assertRaises(ValueError) as context:
            _ = skin_type_handler.skin_regions
        
        self.assertIn("Invalid skin type", str(context.exception))

    def test_auto_detect_skin_type_regular(self):
        """Test automatic detection of regular skin type."""
        skin_type_detector = MCSkinType()
        
        # 创建一个regular类型的皮肤(64x64)
        regular_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        
        # 在右臂边缘添加可见像素以标识为regular类型
        for x in range(44, 52):
            for y in range(16, 20):
                regular_skin.putpixel((x, y), (0, 255, 0, 255))
        
        detected_type = skin_type_detector.auto_detect_skin_type(regular_skin)
        self.assertEqual(detected_type, 'regular')

    def test_auto_detect_skin_type_slim(self):
        """Test automatic detection of slim skin type."""
        skin_type_detector = MCSkinType()
        
        # 创建一个slim类型的皮肤(64x64)
        slim_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        
        detected_type = skin_type_detector.auto_detect_skin_type(slim_skin)
        self.assertEqual(detected_type, 'slim')
    
    def test_convert_skin_64x32_to_64x64(self):
        """Test conversion from 64x32 to 64x64."""
        result = self.skin_tools.convert_skin_64x32_to_64x64(self.test_img_64x32)
        
        # 验证输出尺寸
        self.assertEqual(result.size, (64, 64))
        
        # 验证某些像素是否正确转换
        self.assertEqual(result.getpixel((8, 0)), (0, 255, 0, 255))  # 原始绿色方块应保留
        self.assertEqual(result.getpixel((0, 32)), (0, 0, 0, 0))     # 新区域应透明
        self.assertEqual(result.getpixel((40, 20)), (255, 255, 0, 255))  # 原始黄色方块应保留
        self.assertEqual(result.getpixel((32, 52)), (255, 255, 0, 255))  # 新区域手部黄色方块应复制
    
    def test_swap_skin_layer2_to_layer1(self):
        """Test swapping layers."""
        result = self.skin_tools.swap_skin_layer2_to_layer1(self.test_img_64x64)
        
        # 验证输出尺寸
        self.assertEqual(result.size, (64, 64))

        # 验证某些像素是否正确转换
        self.assertEqual(result.getpixel((8, 0)), (255, 0, 0, 255)) # 第一层应等于红色方块
        self.assertEqual(result.getpixel((40, 0)), (0, 255, 0, 255))  # 第二层应等于绿色方块

    
    def test_remove_layer(self):
        """Test removing layers."""
        # 测试移除第一层
        result_layer1 = self.skin_tools.remove_layer(self.test_img_64x64, 1)
        self.assertEqual(result_layer1.size, (64, 64))
        self.assertEqual(result_layer1.getpixel((8, 0)), (0, 0, 0, 0)) # 第一层应透明
        
        # 测试移除第二层
        result_layer2 = self.skin_tools.remove_layer(self.test_img_64x64, 2)
        self.assertEqual(result_layer2.size, (64, 64))
        self.assertEqual(result_layer2.getpixel((40, 0)), (0, 0, 0, 0)) # 第二层应透明
        
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

    def test_convert_skin_type(self):
        """Test skin type conversion."""

        skin_type_detector = MCSkinType()

        # 创建一个regular类型的皮肤(64x64)
        regular_skin = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        
        # 在右臂添加可见像素以标识为regular类型
        for x in range(44, 52):
            for y in range(16, 20):
                regular_skin.putpixel((x, y), (0, 255, 0, 255))

        # 测试regular转换为slim
        result_slim = self.skin_tools.convert_skin_type(regular_skin, target_type='slim')
        result_type = skin_type_detector.auto_detect_skin_type(result_slim)
        self.assertEqual(result_slim.size, (64, 64))
        self.assertEqual(result_type, 'slim')
        
        # 测试slim转换为regular
        result_regular = self.skin_tools.convert_skin_type(result_slim, target_type='regular')
        result_type = skin_type_detector.auto_detect_skin_type(result_regular)
        self.assertEqual(result_regular.size, (64, 64))
        self.assertEqual(result_type, 'regular')


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
        self.test_img_64x32 = Image.new('RGBA', (64, 32), (255, 0, 0, 255))  # 红色方块
        # 添加一些可识别的像素以便验证转换
        # head1_layer1
        for x in range(8, 24):
            for y in range(0, 8):
                self.test_img_64x32.putpixel((x, y), (0, 255, 0, 255))  # 绿色方块

        
        # right_arm2_layer1
        for x in range(40, 56):
            for y in range(20, 32):
                self.test_img_64x32.putpixel((x, y), (255, 255, 0, 255))  # 黄色方块
        
        # 创建一个64x64测试图像
        self.test_img_64x64 = Image.new('RGBA', (64, 64), (255, 0, 0, 255))  # 红色方块

        # head1_layer1
        for x in range(8, 24):
            for y in range(0, 8):
                self.test_img_64x64.putpixel((x, y), (0, 255, 0, 255))  # 绿色方块

        
        # right_arm2_layer1
        for x in range(40, 56):
            for y in range(20, 32):
                self.test_img_64x64.putpixel((x, y), (255, 255, 0, 255))  # 黄色方块

        # left_arm2_layer1
        for x in range(32, 48):
            for y in range(52, 64):
                self.test_img_64x64.putpixel((x, y), (255, 255, 0, 255))  # 黄色方块
        
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
            self.assertEqual(result_img.getpixel((8, 0)), (0, 255, 0, 255))  # 原始绿色方块应保留
            self.assertEqual(result_img.getpixel((0, 32)), (0, 0, 0, 0))     # 新区域应透明
            self.assertEqual(result_img.getpixel((40, 20)), (255, 255, 0, 255))  # 原始黄色方块应保留
            self.assertEqual(result_img.getpixel((32, 52)), (255, 255, 0, 255))  # 新区域手部黄色方块应复制
    
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
            self.assertEqual(result_img.getpixel((8, 0)), (255, 0, 0, 255)) # 第一层应等于红色方块
            self.assertEqual(result_img.getpixel((40, 0)), (0, 255, 0, 255))  # 第二层应等于绿色方块
    
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
            self.assertEqual(result_img.getpixel((8, 0)), (0, 0, 0, 0)) # 第一层应透明
    
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