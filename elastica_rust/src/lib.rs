use pyo3::prelude::*;

pub fn sum_two(a: i32, b: i32) -> i32 {
    a + b
}

#[pyfunction]
fn add_py(a: i32, b: i32) -> PyResult<i32> {
    Ok(sum_two(a, b))
}

#[pymodule]
fn elastica_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add_py, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sum_two() {
        assert_eq!(sum_two(2, 3), 5);
    }
}
