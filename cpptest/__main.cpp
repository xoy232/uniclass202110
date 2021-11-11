#define BOOST_PYTHON_STATIC_LIB
#define BOOST_LIB_NAME "boost_numpy35"
#include <boost/config/auto_link.hpp>
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <iostream>
#include <opencv2/opencv.hpp>

namespace py = boost::python;
namespace np = boost::python::numpy;

void Init() {
    // set your python location.
    wchar_t str[] = L"D:\\Anaconda3\\envs\\tensorflow_vision";

    Py_SetPythonHome(str);

    Py_Initialize();
    np::initialize();
}

np::ndarray ConvertMatToNDArray(const cv::Mat& mat) {
    py::tuple shape = py::make_tuple(mat.rows, mat.cols, mat.channels());
    py::tuple stride = py::make_tuple(mat.channels() * mat.cols * sizeof(uchar), mat.channels() * sizeof(uchar), sizeof(uchar));
    np::dtype dt = np::dtype::get_builtin<uchar>();
    np::ndarray ndImg = np::from_data(mat.data, dt, shape, stride, py::object());

    return ndImg;
}

cv::Mat ConvertNDArrayToMat(const np::ndarray& ndarr) {
    //int length = ndarr.get_nd(); // get_nd() returns num of dimensions. this is used as a length, but we don't need to use in this case. because we know that image has 3 dimensions.
    const Py_intptr_t* shape = ndarr.get_shape(); // get_shape() returns Py_intptr_t* which we can get the size of n-th dimension of the ndarray.
    char* dtype_str = py::extract<char *>(py::str(ndarr.get_dtype()));

    // variables for creating Mat object
    int rows = shape[0];
    int cols = shape[1];
    int channel = shape[2];
    int depth;

    // you should find proper type for c++. in this case we use 'CV_8UC3' image, so we need to create 'uchar' type Mat.
    if (!strcmp(dtype_str, "uint8")) {
        depth = CV_8U;
    }
    else {
        std::cout << "wrong dtype error" << std::endl;
        return cv::Mat();
    }

    int type = CV_MAKETYPE(depth, channel); // CV_8UC3

    cv::Mat mat = cv::Mat(rows, cols, type);
    memcpy(mat.data, ndarr.get_data(), sizeof(uchar) * rows * cols * channel);

    return mat;
}

int main()
{
    using namespace std;

    try
    {
        // initialize boost python and numpy
        Init();

        // import module
        py::object main_module = py::import("__main__");
        py::object print = main_module.attr("__builtins__").attr("print"); // this is for printing python object

        // get image
        cv::Mat img;
        img = cv::imread("Lenna.jpg", cv::IMREAD_COLOR);
        if (img.empty())
        {
            std::cout << "can't getting image" << std::endl;
            return -1;
        }

        // convert Mat to NDArray
        cv::Mat cloneImg = img.clone(); // converting functions will access to same data between Mat and NDArray. so we should clone Mat object. This may important in your case.
        np::ndarray ndImg = ConvertMatToNDArray(cloneImg);

        // You can check if it's properly converted.
        //print(ndImg);

        // convert NDArray to Mat
        cv::Mat matImg = ConvertNDArrayToMat(ndImg); // also you can convert ndarray to mat.

        // add 10 brightness to converted image
        for (int i = 0; i < matImg.rows; i++) {
            for (int j = 0; j < matImg.cols; j++) {
                for (int c = 0; c < matImg.channels(); c++) {
                    matImg.at<cv::Vec3b>(i, j)[c] += 10;
                }
            }
        }

        // show image
        cv::imshow("original image", img);
        cv::imshow("converted image", matImg);
        cv::waitKey(0);
        cv::destroyAllWindows();
    }
    catch (py::error_already_set&)
    {
        PyErr_Print();
        system("pause");
    }

    system("pause");
    return 0;
}