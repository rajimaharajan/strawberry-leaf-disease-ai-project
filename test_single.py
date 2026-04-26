import sys
from pathlib import Path

from predict import predict_image


def main():
    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
        if not image_path.exists():
            print(f'Error: file not found: {image_path}')
            sys.exit(1)
    else:
        print('Usage: python test_single.py path/to/image.jpg')
        sys.exit(1)

    heatmap_path = image_path.with_stem(image_path.stem + "_heatmap")
    predicted_class, confidence = predict_image(image_path, save_heatmap_path=heatmap_path)
    print(f'Prediction for {image_path.name}: {predicted_class} ({confidence:.2f}%)')
    print(f'Heatmap saved to: {heatmap_path}')


if __name__ == '__main__':
    main()
