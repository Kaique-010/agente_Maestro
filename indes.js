import React, { useState } from 'react'
import {
  View,
  Text,
  TextInput,
  Button,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native'
import { apiPostComContexto } from '../utils/api'
import useContextApp from '../hooks/useContextoApp'
const FormPedidoVenda = ({ pedidoAtual, onSalvar }) => {
  const { empresaId, filialId, usuario_id } = useContextApp()
  const [loading, setLoading] = useState(false)
  const [pedido, setPedido] = useState({
    pedi_forn: pedidoAtual ? pedidoAtual.pedi_forn : '',
    pedi_vend: pedidoAtual ? pedidoAtual.pedi_vend : '',
    pedi_tota: pedidoAtual ? pedidoAtual.pedi_tota : '',
    pedi_data: pedidoAtual
      ? pedidoAtual.pedi_data
      : new Date().toISOString().slice(0, 10),
    pedi_obse: pedidoAtual ? pedidoAtual.pedi_obse : '',
  })
  const handleChange = (name, value) => {
    setPedido({ ...pedido, [name]: value })
  }
  const handleSubmit = async () => {
    if (!pedido.pedi_forn || !pedido.pedi_vend || !pedido.pedi_tota) {
      Alert.alert('Erro', 'Todos os campos são obrigatórios.')
      return
    }
    setLoading(true)
    try {
      const response = await apiPostComContexto('pedidos/', {
        ...pedido,
        empresa: empresaId,
        filial: filialId,
        operador: usuario_id,
      })
      onSalvar(response.data)
      Alert.alert('Sucesso', 'Pedido salvo com sucesso!')
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível salvar o pedido.')
    } finally {
      setLoading(false)
    }
  }
  return (
    <View style={styles.container}>
      {' '}
      <Text style={styles.title}>Formulário de Pedido de Venda</Text>{' '}
      <TextInput
        style={styles.input}
        placeholder="Cliente"
        value={pedido.pedi_forn}
        onChangeText={(value) => handleChange('pedi_forn', value)}
      />{' '}
      <TextInput
        style={styles.input}
        placeholder="Vendedor"
        value={pedido.pedi_vend}
        onChangeText={(value) => handleChange('pedi_vend', value)}
      />{' '}
      <TextInput
        style={styles.input}
        placeholder="Total"
        value={pedido.pedi_tota}
        keyboardType="numeric"
        onChangeText={(value) => handleChange('pedi_tota', value)}
      />{' '}
      <TextInput
        style={styles.input}
        placeholder="Data"
        value={pedido.pedi_data}
        onChangeText={(value) => handleChange('pedi_data', value)}
      />{' '}
      <TextInput
        style={styles.input}
        placeholder="Observações"
        value={pedido.pedi_obse}
        onChangeText={(value) => handleChange('pedi_obse', value)}
      />{' '}
      <Button
        title={loading ? 'Salvando...' : 'Salvar Pedido'}
        onPress={handleSubmit}
        disabled={loading}
      />{' '}
      {loading && <ActivityIndicator size="large" color="#0000ff" />}{' '}
    </View>
  )
}
const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 20 },
  input: {
    height: 40,
    borderColor: '#ccc',
    borderWidth: 1,
    marginBottom: 15,
    paddingHorizontal: 10,
  },
})
export default FormPedidoVenda
